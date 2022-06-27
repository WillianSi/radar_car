from ast import If
from encodings import search_function
import pytesseract
import cv2
import datetime

def desenhaContornos(contornos, imagem):
    for c in contornos:
        # perimetro do contorno, verifica se o contorno é fechado
        perimetro = cv2.arcLength(c, True)
        if perimetro > 120:
            # aproxima os contornos da forma correspondente
            approx = cv2.approxPolyDP(c, 0.03 * perimetro, True)
            # verifica se é um quadrado ou retangulo de acordo com a qtd de vertices
            if len(approx) == 4:
                # Contorna a placa atraves dos contornos encontrados
                (x, y, lar, alt) = cv2.boundingRect(c)
                cv2.rectangle(imagem, (x, y), (x + lar, y + alt), (0, 255, 0), 2)
                # segmenta a placa da imagem
                roi = imagem[y:y + alt, x:x + lar]
                cv2.imwrite("output/roi.png", roi)

def buscaRetanguloPlaca(source):
    # Captura ou Video
    video = cv2.VideoCapture(source)
    i = 0
    while video.isOpened():

        ret, frame = video.read()

        if (ret == False):
            break


        # area de localização u 720p
        area = frame[500:, 300:800]

        # area de localização 480p
        # area = frame[350:, 220:500]

        # escala de cinza
        img_result = cv2.cvtColor(area, cv2.COLOR_BGR2GRAY)

        # limiarização
        ret, img_result = cv2.threshold(img_result, 90, 255, cv2.THRESH_BINARY)

        # desfoque
        img_result = cv2.GaussianBlur(img_result, (5, 5), 0)
        
        cv2.imshow('RES', img_result)

        # lista os contornos
        contornos, hier = cv2.findContours(img_result, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        # limite horizontal
        cv2.line(frame, (0, 500), (1280, 500), (0, 0, 255), 1)
        # limite vertical 1
        cv2.line(frame, (300, 0), (300, 720), (0, 0, 255), 1)
        # limite vertical 2
        cv2.line(frame, (800, 0), (800, 720), (0, 0, 255), 1)

        cv2.imshow('FRAME', frame)

        desenhaContornos(contornos, area)

        cv2.imshow('RES', area)

        if cv2.waitKey(1) & 0xff == ord('q'):
            break

    video.release()
    preProcessamentoRoi()
    cv2.destroyAllWindows()

def preProcessamentoRoi():
    img_roi = cv2.imread("output/roi.png")
    # cv2.imshow("ENTRADA", img_roi)
    if img_roi is None:
        return

    # redmensiona a imagem da placa em 4x
    img = cv2.resize(img_roi, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)

    # Converte para escala de cinza
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("Escala Cinza", img)

    # Binariza imagem
    _, img = cv2.threshold(img, 56, 255, cv2.THRESH_BINARY)
    cv2.imshow("Limiar", img)

    # Desfoque na Imagem
    img = cv2.GaussianBlur(img, (5, 5), cv2.BORDER_REFLECT101)
    # cv2.imshow("Desfoque", img)

    # Aplica reconhecimento OCR no ROI com o Tesseract
    cv2.imwrite("output/roi-ocr.png", img)

    return img

def reconhecimentoOCR():
    img_roi_ocr = cv2.imread("output/roi-ocr.png")
    if img_roi_ocr is None:
        return

    caminho = r'C:\Users\Willian Silvestre\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
    pytesseract.pytesseract.tesseract_cmd = caminho
    config = r'-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 --psm 6'
    saida = pytesseract.image_to_string(img_roi_ocr, lang='eng', config=config)

    # print("Leitura da placa: " + saida)
    return saida

def validate_plate(plate, authorized_plate):
    if plate in authorized_plate:
        return 'Oficial'
    else:
        return 'Nao oficial'

def procurado_plate(plate, search_place):
    if plate in search_place:
        return 'Procurado'
    else:
        return 'Nao procurado'

def date_veiculo(numero, plates):
    if numero in plates:
        agora = datetime.datetime.now()
        dataSaida = agora.strftime("%d/%m/%Y")
        print(dataSaida)
        horaSaida = agora.strftime("%H : %M")
        plates.remove(numero)
        print('saida')
        return horaSaida
           
    else:
        agora = datetime.datetime.now()
        horaEntrada = agora.strftime("%H : %M")
        dataEntrada = agora.strftime("%d/%m/%Y")
        print(dataEntrada)
        plates.append(numero)
        print('entrada')
        return horaEntrada

if __name__ == "__main__":
    source = "resource/video720p.mkv"

    authorized_plate = ['FUN-0972', 'BRA2E19']
    search_place = ['FUN-0972', 'OJJ3984']
    plates = ['FUN-0972', 'OJJ3984']

    #buscaRetanguloPlaca(source)
    #preProcessamentoRoi()
    
    numero = reconhecimentoOCR()
    numero = numero.strip('\n')   

    hora = date_veiculo(numero,plates)

    for i in range(len(plates)):
        oficialVeiculo = validate_plate(plates[i], authorized_plate)
    
    for i in range(len(plates)):
        procuradoVeiculo = procurado_plate(plates[i], search_place)

    print(hora)
    print(numero)
    print(oficialVeiculo)
    print(procuradoVeiculo)
