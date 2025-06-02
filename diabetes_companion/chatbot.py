from langdetect import detect
from deep_translator import GoogleTranslator

def is_arabic(text):
    """Check if text is mostly Arabic."""
    try:
        return detect(text) == 'ar'
    except:
        return False

def translate_to_english(text):
    if is_arabic(text):
        translated = GoogleTranslator(source='ar', target='en').translate(text)
        return translated, 'ar'
    return text, 'en'

def translate_response(text, lang):
    if lang == 'ar':
        return GoogleTranslator(source='en', target='ar').translate(text)
    return text


def clean_response(text):
    text = text.replace("\\n", "")  
    text = text.replace("\n*", "")  
    text = text.replace("\n", "")  
    text = text.replace("\\", "")  
    text = text.replace("*", "")    
    return text.strip()

class DiabetesChatbot:
    def __init__(self, retriever, llm, supabase_client=None):
        self.retriever = retriever
        self.llm = llm
        self.supabase_client = supabase_client
        self.chat_histories = {}  # Store chat history per patient/user_id

    def get_patient_data(self, patient_id):
        if self.supabase_client is None or patient_id is None:
            return {}

        glucose_readings = self.supabase_client.get_glucose_readings(patient_id)
        insulin_doses = self.supabase_client.get_insulin_doses(patient_id)
        meal_logs = self.supabase_client.get_meal_log(patient_id)

        # Simplified summary or formatted string of recent data:
        patient_data = f"Recent glucose readings: {glucose_readings[-5:]}\n"
        patient_data += f"Recent insulin doses: {insulin_doses[-5:]}\n"
        patient_data += f"Recent meals logged (carbs): {meal_logs[-5:]}\n"
        return patient_data

    def build_prompt(self, user_input, patient_id=None):
        # Retrieve chat history for patient/user if exists
        history = self.chat_histories.get(patient_id, [])
        
        # Retrieve patient data
        patient_data = self.get_patient_data(patient_id)

        # Retrieve relevant knowledge docs from retriever
        relevant_docs = self.retriever.get_relevant_documents(user_input)
        context = "\n".join([doc.page_content for doc in relevant_docs[:3]])

        # Build conversation history text (last 3 exchanges)
        history_text = ""
        if history:
            last_exchanges = history[-6:]  # assume user+assistant messages interleaved
            for speaker, text in last_exchanges:
                prefix = "User:" if speaker == "human" else "Assistant:"
                history_text += f"{prefix} {text}\n"

        # Compose the full prompt
        prompt = f"""
You are a diabetes companion assistant specialized ONLY in diabetes. Do NOT give medical advice.

Patient data:
{patient_data}

Relevant information:
{context}

Conversation history:
{history_text}

User question:
{user_input}

Answer:"""
        return prompt.strip()

    def chat(self, user_input, patient_id=None):
        translated_input, source_lang = translate_to_english(user_input)
        prompt = self.build_prompt(translated_input, patient_id)

        messages = [
            ("system", """You are a helpful diabetes companion assistant specialized ONLY in diabetes.
            - NEVER give medical advice.
            - NEVER recommend a specific insulin dose.
            - If the user asks for a dosage, explain the general calculation method (e.g., TDD = weight * 0.55, ISF = 1500/TDD, etc.).
            - Make sure to say that only their doctor or the app’s dosage system can provide exact recommendations."""),
            ("human", prompt)
        ]

        response = self.llm.invoke(messages)
        answer = response.content if response and hasattr(response, "content") else "Sorry, I couldn't answer that."
        answer = clean_response(answer)
        final_answer = translate_response(answer, source_lang)

        # Update chat history per patient_id
        if patient_id:
            if patient_id not in self.chat_histories:
                self.chat_histories[patient_id] = []
            self.chat_histories[patient_id].append(("human", user_input))
            self.chat_histories[patient_id].append(("assistant", final_answer))

        # Store full conversation to database (e.g., Supabase or any other storage layer)
        # self.supabase_client.save_chat_history(patient_id, self.chat_histories[patient_id])

        return final_answer
