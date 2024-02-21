# main.py
import pandas as pd
from urllib.parse import urlparse
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
#from Screenshot import Screenshot
from web_scraper import WebScraper
from image_analysis import analyze_image_for_criteria
from text_detection import TextDetector
from text_generation import TextGenerator
from data_manager import DataManager
import app_ui
from config import GOOGLE_PROJECT_ID, VERTEX_AI_REGION
import os
import google.generativeai as genai
import os
import zipfile
import tempfile
def concatenate_prompt_dicts(dict1, dict2):
    """
    Concatenates the lists of values in two dictionaries based on matching keys.

    :param dict1: First dictionary with lists as values.
    :param dict2: Second dictionary with lists as values.
    :return: Concatenated dictionary.
    """
    concatenated_dict = dict1.copy()  # Copy the first dictionary to avoid modifying the original

    for key, value in dict2.items():
        if key in concatenated_dict:
            concatenated_dict[key].extend(value)
        else:
            concatenated_dict[key] = value

    return concatenated_dict


#genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.markdown('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">', unsafe_allow_html=True)

st.markdown("""
<nav class="navbar fixed-top navbar-expand-lg navbar-dark" style="background-color: #3498DB;">
  <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
    <span class="navbar-toggler-icon"></span>
  </button>
  <div class="collapse navbar-collapse" id="navbarNav">
    <ul class="navbar-nav">
      <li class="nav-item active">
        <a class="nav-link disabled" href="#">Home <span class="sr-only">(current)</span></a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="https://youtube.com/dataprofessor" target="_blank">YouTube</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="https://twitter.com/thedataprof" target="_blank">Twitter</a>
      </li>
    </ul>
  </div>
</nav>
""", unsafe_allow_html=True)


def get_prompts_for_all(country):
    All_prompts = {
            "Germany": [
            "Determine if theres any mention of trusted shops logos or badge (not idealo or similar but real trusted shops logo verified). Reply yes or no. If yes, give details ",
            "Determine if the following text is in German.s Respond with 'yes' or 'no' and briefly explain your reasoning in one sentence:,give details ",
            "Identify any occurrences of 'sale', 'Rabatt', 'Ermäßigung', or 'Schlussverkauf', or similar terms in English or German in the text. Respond 'yes' or 'no'. If 'yes',give details ",
            "Search for terms related to returns like 'return', 'Rücksendung', 'Rückversand', 'Rückgabe', 'Rücksendung Informationen', 'Rückerstattung', or similar in English or German. Reply 'yes' or 'no'. If 'yes', locate these terms in the text, give the original German text,give details",
            "Look for phrases like 'free returns', 'Rücksendung kostenlos', 'Kostenlose Lieferung und Rücksendung', or similar in English or German. Answer 'yes' or 'no'. If 'yes', mention where they are found in the text,give details",
            "Assess if the following text contains delivery-related information. Reply with 'yes' or 'no'. If 'yes', summarize the delivery details:,give details ",
            "Search for 'free delivery', 'Kostenlose Lieferung', 'gratisversand', 'Standardlieferung - Kostenlos ab', 'Kostenfreier Versand', 'Kostenloser Versand ab', or similar terms in English or German. Respond 'yes' or 'no'. If 'yes'.give details ",
            "Identify if there are any instances of FAQ, 'Fragen und Antworten', or 'Fragen & Antworten', or similar in English or German. Answer 'yes' or 'no'. If 'yes', locate these in the text, provide the original German phrase,give details ",
            "Check if there's a phone number in the text. Answer 'yes' or 'no'. If 'yes', please provide the phone number:,give details ",
            "Scan for delivery logos: DHL, Hermes, DPD, UPS, FedEx, Deutsche Post. Yes or no? If yes, which ones,give details",
            "are there visa,mastercard,paypal logos in this image ? if yes tell me what ar they",
            "Look for payment logos: Klarna, Sofort, Giropay. Are they in the image? If yes, identify brands.give details",
            "Look for chat support icons , Are they in the image?, start the answer with yes or no ,give details"
        


    ],
        "Spain" : ["Check if the logos for 'Trustpilot', 'Avis Verifies', or 'Google Reviews' are present in the image. Give details.",
        'Determine if the text in the image is in Spanish. Give details.',
        "Identify any occurrences of 'sale', 'venta', 'rebajas', 'oferta', 'descuento', or 'promoción' in the text. Give details.",
        "Search for terms related to returns like 'return', 'devolución', 'retorno', or 'regreso' in the text. Give details.",
        "Look for phrases like 'free returns', 'devolución gratuita', 'devolución gratis', or 'retorno gratuito' in the text. Give details.",
        "Assess if the text contains the word 'delivery', 'entrega', or 'envío'. Give details.",
        "Check for mentions of 'free delivery', 'entrega gratuita', 'entrega gratis', or 'envío gratis' in the text. Give details.",
        "Identify if there are any instances of 'FAQ', 'preguntas frecuentes', 'P+F', or 'preguntas más comunes' in the text. Give details.",
        "Check if there's a phone number in the text. Give details.",
        'Scan for Spanish delivery company logos: Correos, SEUR, MRW, DHL, UPS. Give details.',
        'Detect payment logos: Visa, Mastercard, PayPal. Give details.',
        'Look for the Bizum payment logo. Give details.',
        'Identify if there is a chat support icon in the image. Give details.'],

        "France" : ["Check if the logos for 'Avis Verifies', 'Google Reviews', or 'TrustPilot' are present in the image. Give details.",
        "Determine if the text in the image is in French. Reply with 'yes' or 'no' and briefly explain your reasoning. Give details.",
        "Identify any occurrences of 'sale', 'soldes', 'promotions', 'rabais', or 'offres spéciales' in the text. Answer 'yes' or 'no'. If 'yes', indicate their location in the text, provide the French phrases, and specify their position in the OCR-extracted image. Give details.",
        "Search for terms related to returns like 'return', 'retour', 'renvoi', or 'remboursement' in the text. Respond 'yes' or 'no'. If 'yes', locate these terms in the text, give the French phrases, and describe their location in the OCR-extracted image. Give details.",
        "Look for phrases like 'free returns', 'retour gratuit', 'renvoi gratuit', or 'remboursement sans frais' in the text. Answer 'yes' or 'no'. If 'yes', mention where they are found in the text, provide the French phrases, and their location in the OCR-extracted image. Give details.",
        "Assess if the text contains the words 'delivery', 'livraison', 'remise', or 'distribution'. Reply with 'yes' or 'no'. If 'yes', summarize the delivery details. Give details.",
        "Check for mentions of 'free delivery', 'livraison gratuite', 'livraison offerte', or 'frais de port offerts' in the text. Respond 'yes' or 'no'. If 'yes', specify their location in the text, include the French phrases, and indicate their position in the OCR-extracted image. Give details.",
        "Identify if there are any instances of 'FAQ', 'questions fréquentes', or 'questions courantes' in the text. Answer 'yes' or 'no'. If 'yes', locate these in the text, provide the French phrases, and their location in the OCR-extracted image. Give details.",
        "Check if there's a phone number in the text. Answer 'yes' or 'no'. If 'yes', please provide the phone number. Give details.",
        'Detect payment logos: Visa, Mastercard, PayPal. Are these logos in the image? If yes, specify which brands are present and their locations. Give details.',
        'Look for the Carte Bancaire payment logo. Is it present in the image? If yes, identify its location. Give details.',
        "Check for the presence of the text 'FAQ' or its French equivalents 'questions fréquentes' or 'questions courantes' in the image. If found, specify the location of the text. Give details.",
        'Identify if there is a chat support icon in the image. If yes, locate and describe its position. Give details.'],

        "Brazil" : ["Check if the logos for 'Trustpilot', 'Google Reviews', 'Reclame Aqui', 'Ebit', or 'Opinion Box' are present in the image. Give details.",
        "Determine if the text in the image is in Portuguese. Reply with 'yes' or 'no' and briefly explain your reasoning. Give details.",
        "Identify any occurrences of 'sale', 'liquidação', 'promoção', 'oferta', or 'desconto' in the text. Answer 'yes' or 'no'. If 'yes', indicate their location in the text, provide the Portuguese phrases, and specify their position in the OCR-extracted image. Give details.",
        "Search for terms related to returns like 'return', 'devolução', 'troca', or 'reembolso' in the text. Respond 'yes' or 'no'. If 'yes', locate these terms in the text, give the Portuguese phrases, and describe their location in the OCR-extracted image. Give details.",
        "Look for phrases like 'free returns', 'devolução gratuita', 'devolução grátis', 'troca gratuita', or 'frete de devolução grátis' in the text. Answer 'yes' or 'no'. If 'yes', mention where they are found in the text, provide the Portuguese phrases, and their location in the OCR-extracted image. Give details.",
        "Assess if the text contains any of these words 'delivery', 'entrega', 'remesa', or 'frete'. Reply with 'yes' or 'no'. If 'yes', summarize the delivery details. Give details.",
        "Check for mentions of 'free delivery', 'frete grátis', 'entrega grátis', or 'entrega gratuita' in the text. Respond 'yes' or 'no'. If 'yes', specify their location in the text, include the Portuguese phrases, and indicate their position in the OCR-extracted image. Give details.",
        "Identify if there are any instances of 'FAQ', 'perguntas frequentes', 'dúvidas frequentes', or 'perguntas e respostas' in the text. Answer 'yes' or 'no'. If 'yes', locate these in the text, provide the Portuguese phrases, and their location in the OCR-extracted image. Give details.",
        "Check if there's a phone number in the text. Answer 'yes' or 'no'. If 'yes', please provide the phone number. Give details.",
        'Detect payment logos: Visa, Mastercard, PayPal. Are these logos in the image? If yes, specify which brands are present and their locations. Give details.',
        'Look for payment logos: Elo, Hipercard, boleto bancário, PIX. Are these logos in the image? If yes, specify which brands are present and their locations. Give details.',
        "Check for the presence of the text 'FAQ' or its Portuguese equivalents 'perguntas frequentes', 'dúvidas frequentes', or 'perguntas e respostas' in the image. If found, specify the location of the text. Give details.",
        'Identify if there is a chat support icon in the image. If yes, locate and describe its position. Give details.'],

        "Italy" : [
        "Verifique se o logotipo do 'TrustPilot', 'Google Recensioni' ou 'Altroconsumo' está presente ou não visualmente. Responda 'sim' ou 'não' e forneça detalhes no final.",
        "Determine se o texto na imagem está em italiano. Responda com 'sim' ou 'não' e explique brevemente seu raciocínio.",
        "Identifique quaisquer ocorrências de 'sale', 'saldi', 'sconti', 'offerte' ou 'promozioni' no texto. Responda 'sim' ou 'não'. Se sim, indique sua localização no texto, forneça as frases em italiano e especifique sua posição na imagem extraída por OCR.",
        "Procure por termos relacionados a devoluções como 'return', 'reso', 'restituzione' ou 'rimborso' no texto. Responda 'sim' ou 'não'. Se sim, localize esses termos no texto, forneça as frases em italiano e descreva sua localização na imagem extraída por OCR.",
        "Procure por frases como 'free returns', 'reso gratuito', 'reso gratis' ou 'restituzione gratuita' no texto. Responda 'sim' ou 'não'. Se sim, mencione onde são encontrados no texto, forneça as frases em italiano e sua localização na imagem extraída por OCR.",
        "Avalie se o texto contém alguma destas palavras 'delivery', 'consegna', 'spedizione' ou 'recapito'. Responda 'sim' ou 'não'. Se sim, resuma os detalhes da entrega.",
        "Verifique as menções de 'free delivery', 'spedizione gratuita' ou 'consegna gratuita' no texto. Responda 'sim' ou 'não'. Se sim, especifique sua localização no texto, inclua as frases em italiano e indique sua posição na imagem extraída por OCR.",
        "Identifique se há alguma instância de 'FAQ', 'domande frequenti' no texto. Responda 'sim' ou 'não'. Se sim, localize-as no texto, forneça as frases em italiano e sua localização na imagem extraída por OCR.",
        "Verifique se há um número de telefone no texto. Responda 'sim' ou 'não'. Se sim, forneça o número de telefone.",
        'Detecte logotipos de pagamento: Visa, Mastercard, PayPal. Esses logotipos estão na imagem? Se sim, especifique quais marcas estão presentes e suas localizações.',
        'Procure por logotipos de pagamento: Postepay, Bancomat, Bancomat Pay, o circuito PagoBancomat. Estes logotipos estão na imagem? Se sim, especifique quais marcas estão presentes e suas localizações.',
        "Verifique a presença do texto 'FAQ' ou seu equivalente em italiano 'domande frequenti' na imagem. Se encontrado, especifique a localização do texto.",
        'Identifique se há um ícone de suporte por chat na imagem. Se sim, localize e descreva sua posição.'],

        "UAE" : [
            "Check visually if the logos for 'Google Reviews' (جوجل ريفيوز), 'Trustpilot' (ترست بايلوت), or 'Yallacompare' (يلا كومبير) are present. Respond 'yes' or 'no' and give details at the end.",
            "Determine if the text in the image is in Arabic. Reply with 'yes' or 'no' and briefly explain your reasoning: ",
            "Identify any occurrences of 'sale', 'تخفيضات' (Takhfidat), 'تنزيلات' (Tanzilat), 'عروض' (Urood), 'خصومات' (Khusumat) in the text. Answer 'yes' or 'no'. If 'yes', indicate their location in the text, provide the Arabic phrases, and specify their position in the OCR-extracted image: ",
            "Search for terms related to returns like 'return', 'إرجاع' (Irja'), 'استبدال' (Istibdal), 'استرداد' (Istirdad) in the text. Respond 'yes' or 'no'. If 'yes', locate these terms in the text, give the Arabic phrases, and describe their location in the OCR-extracted image: ",
            "Look for phrases like 'free returns', 'إرجاع مجاني' (Irja' majani), 'استبدال مجاني' (Istibdal majani), 'استرداد مجاني' (Istirdad majani) in the text. Answer 'yes' or 'no'. If 'yes', mention where they are found in the text, provide the Arabic phrases, and their location in the OCR-extracted image: ",
            "Assess if the text contains any of these words 'delivery', 'توصيل' (Tawseel), 'تسليم' (Tasleem), 'شحن' (Shahn). Reply with 'yes' or 'no'. If 'yes', summarize the delivery details: ",
            "Check for mentions of 'free delivery', 'توصيل مجاني' (Tawseel majani), 'شحن مجاني' (Shahn majani) in the text. Respond 'yes' or 'no'. If 'yes', specify their location in the text, include the Arabic phrases, and indicate their position in the OCR-extracted image: ",
            "Identify if there are any instances of 'FAQ', 'الأسئلة الشائعة' (Al-as'ila al-shai'ea), 'الأسئلة المتكررة' (Al-as'ila al-mutakarira) in the text. Answer 'yes' or 'no'. If 'yes', locate these in the text, provide the Arabic phrases, and their location in the OCR-extracted image: ",
            "Check if there's a phone number in the text. Answer 'yes' or 'no'. If 'yes', please provide the phone number: ",
            "Scan for delivery company logos: Aramex (أرامكس), FedEx (فيديكس), DHL, and Emirates Post (بريد الإمارات). Are they present in the image? If yes, identify which logos are visible and their locations.",
            "Detect payment logos: Visa, Mastercard, PayPal. Are these logos in the image? If yes, specify which brands are present and their locations.",
            "Look for payment logos: Cash on Delivery (COD) (الدفع عند الاستلام). Are these logos in the image? If yes, specify their locations.",
            "Identify if there is a chat support icon in the image. If yes, locate and describe its position."

        ],

        "Japan" : [ 
            "Check visually if the logos for 'Google レビュー' (Google rebyu) or '価格.com' (Kakaku.com) are present. Respond 'yes' or 'no' and give details at the end.",
            "Determine if the text in the image is in Japanese. Reply with 'yes' or 'no' and briefly explain your reasoning: ",
            "Identify any occurrences of 'sale', 'セール' (se-ru), 'バーゲン' (ba-gen), '割引' (waribiki), '特売' (tokubai) in the text. Answer 'yes' or 'no'. If 'yes', indicate their location in the text, provide the Japanese phrases, and specify their position in the OCR-extracted image: ",
            "Search for terms related to returns like 'return', '返品' (henpin), '交換' (koukan), '返金' (henkin) in the text. Respond 'yes' or 'no'. If 'yes', locate these terms in the text, give the Japanese phrases, and describe their location in the OCR-extracted image: ",
            "Look for phrases like 'free returns', '返品無料' (henpin muryou), '送料無料返品' (souryou muryou henpin) in the text. Answer 'yes' or 'no'. If 'yes', mention where they are found in the text, provide the Japanese phrases, and their location in the OCR-extracted image: ",
            "Assess if the text contains any of these words 'delivery', '配送' (haisou), '配達' (haitatsu), '発送' (hasou). Reply with 'yes' or 'no'. If 'yes', summarize the delivery details: ",
            "Check for mentions of 'free delivery', '送料無料' (souryou muryou) in the text. Respond 'yes' or 'no'. If 'yes', specify their location in the text, include the Japanese phrases, and indicate their position in the OCR-extracted image: ",
            "Identify if there are any instances of 'FAQ' in the text. Answer 'yes' or 'no'. If 'yes', locate these in the text, provide the Japanese phrases, and their location in the OCR-extracted image: ",
            "Check if there's a phone number in the text. Answer 'yes' or 'no'. If 'yes', please provide the phone number: ",
            "Scan for delivery company logos: ヤマト運輸(Yamato unyu), 佐川急便(Sagawa kyuubin), 日本郵便(ゆうパック) (Nippon yuubin (yuupakku)). Are they present in the image? If yes, identify which logos are visible and their locations.",
            "Detect payment logos: Visa, Mastercard, PayPal. Are these logos in the image? If yes, specify which brands are present and their locations.",
            "Look for payment logos: 各種クレジットカード(kurejitto ka-do: credit cards), コンビニ決済(konbini kesai: convenience store payment), 代金引換(daikin hikikae: cash on delivery). Are these logos in the image? If yes, specify their locations.",
            "Identify if there is a chat support icon in the image. If yes, locate and describe its position."

            ],

        "US" :[
            "Check visually if there are logos for the 'Better Business Bureau', 'Google Reviews', 'Reviews.io', or 'Yotpo' present. Respond 'yes' or 'no' and give details at the end.",
            "Determine if the text in the image is in US English. Reply with 'yes' or 'no' and briefly explain your reasoning: ",
            "Identify any occurrences of 'sale', 'clearance', 'discount', 'promotion' in the text. Answer 'yes' or 'no'. If 'yes', indicate their location in the text and specify their position in the OCR-extracted image: ",
            "Search for terms related to returns like 'returns', 'exchange', or 'refund' in the text. Respond 'yes' or 'no'. If 'yes', locate these terms in the text and describe their location in the OCR-extracted image: ",
            "Look for phrases like 'free returns' or 'hassle-free returns' in the text. Answer 'yes' or 'no'. If 'yes', mention where they are found in the text and their location in the OCR-extracted image: ",
            "Assess if the text contains any of these words 'delivery', 'shipping', or 'fulfillment'. Reply with 'yes' or 'no'. If 'yes', summarize the delivery details: ",
            "Check for mentions of 'free delivery' or 'free shipping' in the text. Respond 'yes' or 'no'. If 'yes', specify their location in the text and indicate their position in the OCR-extracted image: ",
            "Identify if there are any instances of 'FAQ' or 'frequently asked questions' in the text. Answer 'yes' or 'no'. If 'yes', locate these in the text and their location in the OCR-extracted image: ",
            "Check if there's a phone number in the text. Answer 'yes' or 'no'. If 'yes', please provide the phone number: ",
            "Scan for delivery logos: UPS, FedEx, USPS (United States Postal Service). Yes or no? If yes, which and where?",
            "Detect payment logos: Visa, Mastercard, PayPal. Present, yes or no? If yes, specify brands and locations.",
            "Look for payment logos: American Express, Venmo, Cash App. Are they in the image? If yes, identify brands and their locations.",
            "Look for chat support icons. Are they in the image? If yes, identify their locations."

        ]
        }
    return All_prompts.get(country, [])

def get_prompts_for_country_images(country):
    prompts_dict = {
        "Germany": [
        "Scan for delivery logos: DHL, Hermes, DPD, UPS, FedEx, Deutsche Post. Yes or no? If yes, which and where?",
        "Detect payment logos: Visa, Mastercard, PayPal. Present, yes or no? If yes, specify brands and locations.",
        "Look for payment logos: Klarna, Sofort, Giropay. Are they in the image? If yes, identify brands and their locations.",
        "Look for chat support icons , Are they in the image? If yes,  identify their locations."
    ],
        "Spain": [
    "Scan for Spanish delivery company logos: Correos, SEUR, MRW, DHL, UPS. Are they present in the image? If yes, identify which logos are visible and their locations.",
    "Detect payment logos: Visa, Mastercard, PayPal. Are these logos in the image? If yes, specify which brands are present and their locations.",
    "Look for the Bizum payment logo. Is it present in the image? If yes, identify its location.",
    "Identify if there is a chat support icon in the image. If yes, locate and describe its position."
],

    "France" : [
    "Detect payment logos: Visa, Mastercard, PayPal. Are these logos in the image? If yes, specify which brands are present and their locations.",
    "Look for the Carte Bancaire payment logo. Is it present in the image? If yes, identify its location.",
    "Check for the presence of the text 'FAQ' or its French equivalents 'questions fréquentes' or 'questions courantes' in the image. If found, specify the location of the text.",
    "Identify if there is a chat support icon in the image. If yes, locate and describe its position."
],

    "Brazil" : [
    "Detect payment logos: Visa, Mastercard, PayPal. Are these logos in the image? If yes, specify which brands are present and their locations.",
    "Look for payment logos: Elo, Hipercard, boleto bancário, PIX. Are these logos in the image? If yes, specify which brands are present and their locations.",
    "Check for the presence of the text 'FAQ' or its Portuguese equivalents 'perguntas frequentes' or 'dúvidas frequentes' or 'perguntas e respostas' in the image. If found, specify the location of the text.",
    "Identify if there is a chat support icon in the image. If yes, locate and describe its position."
],

    "Italy" :[
    "Detect payment logos: Visa, Mastercard, PayPal. Are these logos in the image? If yes, specify which brands are present and their locations.",
    "Look for payment logos: Postepay, Bancomat, Bancomat Pay, il circuito PagoBancomat. Are these logos in the image? If yes, specify which brands are present and their locations.",
    "Check for the presence of the text 'FAQ' or its Italian equivalent 'domande frequenti' in the image. If found, specify the location of the text.",
    "Identify if there is a chat support icon in the image. If yes, locate and describe its position."
], 

    "UAE" : [
    "Scan for delivery company logos: Aramex (أرامكس), FedEx (فيديكس), DHL, and Emirates Post (بريد الإمارات). Are they present in the image? If yes, identify which logos are visible and their locations.",
    "Detect payment logos: Visa, Mastercard, PayPal. Are these logos in the image? If yes, specify which brands are present and their locations.",
    "Look for payment logos: Cash on Delivery (COD) (الدفع عند الاستلام). Are these logos in the image? If yes, specify their locations.",
    "Identify if there is a chat support icon in the image. If yes, locate and describe its position."
],

    "Japan" : [
    "Scan for delivery company logos: ヤマト運輸(Yamato unyu), 佐川急便(Sagawa kyuubin), 日本郵便(ゆうパック) (Nippon yuubin (yuupakku)). Are they present in the image? If yes, identify which logos are visible and their locations.",
    "Detect payment logos: Visa, Mastercard, PayPal. Are these logos in the image? If yes, specify which brands are present and their locations.",
    "Look for payment logos: 各種クレジットカード(kurejitto ka-do: credit cards), コンビニ決済(konbini kesai: convenience store payment), 代金引換(daikin hikikae: cash on delivery). Are these logos in the image? If yes, specify their locations.",
    "Identify if there is a chat support icon in the image. If yes, locate and describe its position."
],

    "US" : [
    "Scan for delivery logos: UPS, FedEx, USPS (United States Postal Service). Yes or no? If yes, which and where?",
    "Detect payment logos: Visa, Mastercard, PayPal. Present, yes or no? If yes, specify brands and locations.",
    "Look for payment logos: American Express, Venmo, Cash App. Are they in the image? If yes, identify brands and their locations.",
    "Look for chat support icons. Are they in the image? If yes, identify their locations."
]

    
        # ... Add for other countries
    }
    return prompts_dict.get(country, [])


def main():
    os.environ['GRPC_DNS_RESOLVER'] = 'native'

    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] > .main {
        background: linear-gradient(135deg, #ffffff, #e6e8eb);
    }
    .icon {
        font-size: 1.5em;
        vertical-align: middle;
        margin-right: 10px;
    }
    /* Additional styles here */
    </style>
""", unsafe_allow_html=True)


    # Load CSS for the Streamlit app
    app_ui.load_css()
    # Render the UI components
    #app_ui.render_navbar2()
    app_ui.render_header()
    url, selected_country,analyze_button = app_ui.render_input_section2()
    
    xpath_input = st.text_input("Enter XPath")

    # Add button to process with the given XPath
    xpath_button = st.button("Add XPath")

    def process_urls(url,selected_country) : 
        temp_dir = tempfile.mkdtemp()
        file_paths = []
        for index, url in enumerate(url): 
            scraper = WebScraper()
            scraper.handle_cookies(url,xpath_input)
            screenshot_data,screenshot_path = scraper.capture_and_return_fullpage_screenshot(url)
            scraper.close()

                        # Save the screenshot in the temporary directory and add its path to file_paths
            screenshot_file_path = os.path.join(temp_dir, f"screenshot_{index}.png")
            with open(screenshot_file_path, "wb") as file:
                file.write(screenshot_data)
            file_paths.append(screenshot_file_path)
            # Initialize TextDetector and analyze the image for text
            text_detector = TextDetector()
            detected_texts = text_detector.analyze_image_for_text(screenshot_data)
            #text_criteria_results = text_detector.process_detected_text(detected_texts)

            # Initialize TextGenerator and generate text responses
            text_generator = TextGenerator(GOOGLE_PROJECT_ID, VERTEX_AI_REGION)
            #prompts_text =  get_prompts_for_country_text(selected_country)  
            #prompts_images = get_prompts_for_country_images(selected_country)
            #full_text = ' '.join(detected_texts)  # Concatenates all detected text into one string
            #prompts = [prompt.format(full_text=full_text) for prompt in prompts]
            

            # Assuming each 'EntityAnnotation' object has a 'description' attribute with the text content
            extracted_texts = [entity.description for entity in detected_texts if hasattr(entity, 'description')]
            full_text = ' '.join(extracted_texts)  # Concatenates all extracted text into one string

            # Now use 'full_text' in your prompts
            All_prompts = get_prompts_for_all(selected_country)
            #All_prompts = [prompt.format(full_text=full_text) for prompt in All_prompts]


            #parameters = {"temperature": 0.7, "max_output_tokens": 256, "top_p": 0.8, "top_k": 40}
            #text_responses = text_generator.generate_text_responses(prompts, parameters)
            #processed_text_results = text_generator.process_responses(text_responses, prompts)
            #genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

            #All_prompts = concatenate_prompt_dicts(prompts_text, prompts_images)

            # Analyze the image for specific criteria using Image Analysis
            image_analysis_results,split_images_paths = analyze_image_for_criteria(screenshot_path, GOOGLE_PROJECT_ID, VERTEX_AI_REGION,prompts=All_prompts)
            
            for path in split_images_paths :
                for path2 in path : 
                    file_paths.append(path2) 
 

            final_df = pd.DataFrame(columns=['criteria', 'yes/no(1/0)', 'additional_infos'])

            i = 0
            for df in image_analysis_results : 
                # Data Management and Export
                rename_mappings = {'yes or no': 'yes/no(1/0)'}
                convert_columns = {'yes/no(1/0)': lambda x: 1 if str(x).strip().lower() in ['yes', 'true'] else 0}
                df=DataManager.preprocess_dataframe(df,rename_mappings=rename_mappings,convert_columns=convert_columns)
                parsed_url = urlparse(url)
                domain_name = parsed_url.netloc

        # Extracting just the 'kaufland' part from the domain name
                extracted_name = domain_name.split('.')[1] 
                
                df.insert(0, 'Company_Name', extracted_name)

                # Add 'Company_Url' column at the second position
                df.insert(1, 'Company_Url', url)
                
  
                rename = [
                    "Contains Trusted Shops Certification",
                    "Text in German",
                    "Contains Sale or Discount Keywords",
                    "Contains Return Policy Keywords",
                    "Offers Free Returns",
                    "Has Delivery Information",
                    "Mentions Free Delivery",
                    "Contains FAQ or Questions Section",
                    "Includes a Phone Number",
                    "Shows Delivery Companies Logos",
                    "Displays Visa/Mastercard/PayPal Logos",
                    "Displays Klarna/Sofort/Giropay Logos",
                    "Features a Chat Support Icon"
                ]

                df.insert(0, 'Image_Split_Number',i )


                df.index = rename 



                i=i+1
            
                
            final_results = pd.concat(image_analysis_results, axis=0, ignore_index=True)

        #final_results=image_analysis_results[1]
 
            # This assumes the format is [subdomain].[name].[tld]

            xlsx_data = DataManager.convert_df_to_xlsx(final_results)

            xlsx_file_path = os.path.join(temp_dir, f"{extracted_name}.xlsx")
            with open(xlsx_file_path, "wb") as f:
                f.write(xlsx_data)
            file_paths.append(xlsx_file_path)
           

                
            return file_paths


    def make_zip_file(file_paths):
        # Create a temporary file for the zip
        zip_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        zip_file_path = zip_file.name

        with zipfile.ZipFile(zip_file, 'w') as zipf:
            for file in file_paths:
                zipf.write(file, os.path.basename(file))

        return zip_file_path


    if analyze_button and url and xpath_input:

        file_paths = process_urls(url,selected_country)

        zip_file_path = make_zip_file(file_paths)

        with open(zip_file_path, "rb") as f:
            st.download_button(
                label="Download ZIP",
                data=f,
                file_name="all_results.zip",
                mime="application/zip"
            )
        

        # Initialize WebScraper and capture a screenshot
        

        #st.session_state['results_data'][url] = xlsx_data

        # Render the download button for the results
        # Create a unique key for each download button
        #download_button_key = f"download_button_{index}"

        # Render the download button with the unique key
        #app_ui.render_download_button(xlsx_data, key=download_button_key)
    # Outside the if analyze_button block


    #app_ui.render_about_section()
    app_ui.render_footer()

if __name__ == "__main__":
    main()
