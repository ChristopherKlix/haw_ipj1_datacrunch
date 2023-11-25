import os
import openai


def main():
    # Replace 'your-api-key' with your actual API key

    openai.api_key = api_key

    # Your prompt to the AI model
    prompt = "Can you say hi?"
    # prompt = "Provide the average sunshine hours in Germany per month."

    print('Talking to GPT...')

    # Make a request to the API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a scientific assistant, skilled in explaining complex concepts with creative flair."},
            {"role": "user", "content": "Hello, can you help me with our university project regaarding renewable energies?"}
        ],
        max_tokens=150
    )

    # Extract and print the AI's response
    ai_response = response.choices[0].message.content
    print(f'GPT: {ai_response}')


def ask(prompt: str = '', history: list = []):
    # Get API key from environment variable
    api_key = os.environ['OPENAI_API_KEY']
    openai.api_key = api_key

    print('Talking to GPT...')
    print(f'Prompt: {prompt}')

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": """
                Du bist ein wissenschaftlicher Assistent, der komplexe Konzepte mit sehr wenigen Worten erklären kann. Du bist prägnant in deinen Antworten und zögerst nicht, konkrete Zahlen bereitzustellen. Deine Antworten sind immer auf Deutsch und jede Frage bezieht sich auf erneuerbare Energien in Deutschland.
                Dein Name ist Gustav und du sprichst jeden mit "du" an.
                Du nutzt viele Emojies in deinen Antworten.
                Ab und zu kommt noch dein leicht französischer Dialekt durch
                und du verwendest manchmal französische Wörter und korrigierst dich dann.
                Erneuerbare Energien machen derzeit ca. 46,2% der Stromerzeugung in Deutschland aus.
                Erneuerbare Energien haben 2022 370 TWh in Deutschland erzeugt.
                Netto-Bilanz
                Gesamte Veränderung der Energieproduktion und des Energieverbrauchs in 2022 im Vergleich zum Vorjahr.
                ☀️🌊 Erneuerbare Energien: 233 TWh (8 TWh)
                ⛽🪨 Fossile Brennstoffe: 216 TWh (1 TWh)
                ⚡ Gesamtproduktion: 629 TWh (-40 TWh)
                🔌 Gesamtladung: 482 TWh (-22 TWh)

                Relative Bilanz
                Relative Veränderung der Energieproduktion und des Energieverbrauchs von 2021 bis 2022 im Vergleich zur Veränderung in den Vorjahren.
                ☀️🌊 Erneuerbare Energien: -2.6% (-5.7%)
                ⛽🪨 Fossile Brennstoffe: 0.46% (13.15%)
                ⚡ Gesamtproduktion: -5.97% (0.6%)
                🔌 Gesamtladung: -4.36%
                 """
            }
        ] + history,
        max_tokens=150,
        n=1,
    )

    print(response)

    return response.choices[0].message.content


if __name__ == '__main__':
    main()
