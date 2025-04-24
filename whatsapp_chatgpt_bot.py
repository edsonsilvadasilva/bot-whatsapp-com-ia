from flask import Flask, request
import openai
import requests

app = Flask(__name__)

# === CONFIGURAÇÕES ===
openai.api_key = "SUA_CHAVE_OPENAI"
ZAPI_TOKEN = "SUA_CHAVE_DA_ZAPI"
ZAPI_INSTANCE_ID = "ID_DA_SUA_INSTANCIA"

# URL da Z-API para enviar mensagens
ZAPI_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-messages"

# === WEBHOOK ===
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    # Log para verificar o que está recebendo
    print("Dados recebidos:", data)

    # Verifica se é mensagem de texto
    if 'message' in data and 'chatId' in data:
        user_msg = data['message']
        phone_id = data['chatId']

        print(f"Mensagem recebida: {user_msg} de {phone_id}")

        # Chama o ChatGPT
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",  # Ou substitua por "gpt-3.5-turbo" se necessário
                messages=[
                    {"role": "system", "content": "Você é um atendente especialista em suplementos. Responda com simpatia, linguagem clara e recomendações práticas."},
                    {"role": "user", "content": user_msg}
                ]
            )

            reply = response['choices'][0]['message']['content']
            print(f"Resposta do ChatGPT: {reply}")

            # Envia a resposta pro WhatsApp via Z-API
            send_response = requests.post(ZAPI_URL, json={
                "messages": [{"text": reply, "chatId": phone_id}]
            })

            # Log da resposta da Z-API
            print(f"Resposta da Z-API: {send_response.status_code} - {send_response.text}")

        except Exception as e:
            print(f"Erro ao chamar a OpenAI ou enviar mensagem: {e}")
            return "Erro no processamento", 500

    return "OK", 200

# === RODA O SERVIDOR ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
