from PIL import Image
import io

def get_images_from_pdf(pdf_file, verbose: bool = False) -> list:
    # iterate over pdf pages
    image_list_container = []
    for page_index in range(len(pdf_file)):
        # get the page itself
        page = pdf_file[page_index]
        image_list = page.get_images()
        # printing number of images found in this page
        if image_list:
            if verbose:
                print(f"[+] Found a total of {len(image_list)} images in page {page_index}")
        else:
            if verbose:
                print("[!] No images found on page", page_index)
        for image_index, img in enumerate(page.get_images(), start=1):
            # get the XREF of the image
            xref = img[0]
            # extract the image bytes
            base_image = pdf_file.extract_image(xref)
            image_bytes = base_image["image"]
            # get the image extension
            image_ext = base_image["ext"]
            # load it to PIL
            image = Image.open(io.BytesIO(image_bytes))
            filename = f"image_{page_index+1}_{image_index}.{image_ext}"
            image_list_container.append((image_bytes, image, filename))

    pdf_file.close()
    return image_list_container
