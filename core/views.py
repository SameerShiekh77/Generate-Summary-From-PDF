from django.shortcuts import render,redirect,HttpResponseRedirect
from django.urls import reverse
import openai
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io


# Create your views here.
def index(request):
    summary = request.GET.get('summary',"")
    context = {
        'summary':summary
    }
    return render(request, 'index.html',context)


def extract_text_from_pdf(file):
    pdf_document = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        text += page.get_text()

        # Extract images and apply OCR
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]

            # Convert to PIL Image and apply OCR
            image = Image.open(io.BytesIO(image_bytes))
            text += pytesseract.image_to_string(image)

    return text

def generate_mcq_prompt_pdf(file):
    return  f"""
        Read and Analyze this PDF {file}: Thoroughly read the provided PDF document. Ensure to cover all text, charts, tables, and images. Use OCR for Visual Elements: Utilize OCR (Optical Character Recognition) to extract text from charts, tables, and images present in the PDF. Generate a Summary: Create a detailed summary that encompasses all key points, important details, and relevant information from the entire document.
 """

def pdf_summarize(request):
    summary = ""
    context = {
        'summary':summary
        }
    if request.method == 'POST':
        file = request.FILES.get("file")
        extracted_text = extract_text_from_pdf(file)
        openai.api_key = "your-api-key"
        messages = [
            {"role": "system", "content": generate_mcq_prompt_pdf(extracted_text)},
        ]
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=1,
            max_tokens=4000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        messages.append({"role": "assistant", "content": response.choices[0].message["content"]})
        # print(response.choices[0].message["content"])
        summary = response.choices[0].message["content"]
        context['summary'] = summary
        
        return render(request, 'index.html',context)
    return render(request, 'index.html',context)