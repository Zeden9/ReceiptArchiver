import cv2
import easyocr
import re



def preprocess_image(image_path):
    img = cv2.imread(image_path)
    # --- Quality improvement ---
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)  
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)    
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        15, 10
    )
    denoised = cv2.fastNlMeansDenoising(thresh, h=15)
    cv2.imwrite("paragon_clean.jpg", denoised)
    reader = easyocr.Reader(['pl', 'en'], gpu=True)

    return reader.readtext("paragon_clean.jpg")
   
    
def list_products(ocr_result):
    buffer = []
    products = []
    scanBegin = False
    print("===== Odczytany tekst =====")
    for element in ocr_result:
        if (re.findall("FISKALNY", element[-2])):
            scanBegin = True
            continue
        if not scanBegin:
            continue
        buffer.append(element[-2])
        if (re.findall("[0-9][A-G]$", element[-2])):
            products.append(buffer)
            buffer = []

    return products


#print(products)
def standarize_products(products_raw):
    products = []
    for prod in products_raw:
        name = " ".join(prod[:-1])
        price = re.findall(r"\d+,\d{2}", prod[-1])
        if price:
            price = price[-1]
        else:
            price = "BRAK CENY"
        price = float(price.replace(",", "."))
        if re.findall("Rabat", name):
            products[-1][price] = price
            continue
        
        products.append({"name" : name, "price" : price})
        #print(f"Name: {name}, Price: {price}")

    print(products)

if __name__ == "__main__":
    ocr_result = preprocess_image("paragon.jpg")
    products = list_products(ocr_result)
    standarize_products(products)