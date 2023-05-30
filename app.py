import os
import streamlit as st
os.environ["OPENAI_API_KEY"] = st.secrets["OpenAI"]

from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
import re

from streamlit_chat import message as st_message
from streamlit_option_menu import option_menu



def chatbot(pregunta):
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    if "history" not in st.session_state:
        st.session_state['history'] = []
    
    embedding = OpenAIEmbeddings()
    vectordb = Chroma(persist_directory=st.session_state.persist_directory, 
                    embedding_function=embedding)
    qa = ConversationalRetrievalChain.from_llm(ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo"), 
                                               vectordb.as_retriever(search_kwargs={"k":2}), 
                                               return_source_documents=True)
    result = qa({"question": pregunta, "chat_history": st.session_state.chat_history})
    st.session_state.chat_history.append((pregunta, result['answer']))
    st.session_state.history.append({"message": pregunta, "is_user": True})
    result_text = result['answer'] + '\n\n\n'
    
    for source in result["source_documents"]:
        result_text += f"Fuente: {source.metadata['source']}  //  Página: {source.metadata['page']}\n\n Cita: ''{source.page_content}''\n\n"

    st.session_state.history.append({"message": result_text, "is_user": False})
    st.session_state['resultado'] = result
    return




#-----------------------------------------------------------------APP STREAMLIT----------------------------------------------------------------------------------------

#CONFIGURACION DE LA PAGINA
st.set_page_config(page_title="KnowSphere", page_icon="📚", layout="wide")

#MENU LATERAL
with st.sidebar:
   seleccion_menu = option_menu(
      menu_title = "Menu",
      options=["Inicio", "Chat"],
      icons=["house", "chat-right-text-fill"],
      menu_icon = "cast",
      default_index = 0,
   )

#CABECERA
st.markdown(
  """
  <div style='text-align: center;'>
      <h1>📚 KnowSphere 📚</h1>
      <h4> Empoderando a los estudiantes</h4>
  </div>
  """,
    unsafe_allow_html=True
)

st.write("---")

#SELECCION UNIVERSIDAD-GRADO
if seleccion_menu == "Inicio":

    if 'inicio' in st.session_state:
        universidad = st.selectbox(
            'Universidad',
            ('UAM', 'Universidad de Málaga', 'Universidad Europea')
        )

        if universidad == "UAM":
            grado = st.selectbox(
                'Elige la asignatura',
                ('Biología', 'Matemáticas', 'Derecho Internacional', 'Historia')
            )

            if grado == "Biología":
                st.session_state['persist_directory'] = 'apuntes/biologia'
                st.session_state['grado'] = "Biología"
            elif grado == "Derecho Internacional":
                st.session_state['persist_directory'] = 'apuntes/derecho_internacional'
                st.session_state['grado'] = "Derecho Internacional"
            elif grado == "Historia":
                st.session_state['persist_directory'] = 'apuntes/historia'
                st.session_state['grado'] = "Historia"

    if 'inicio' not in st.session_state:
        st.write("## Iniciar Sesión")
        with st.form(key="formulario"):
            usuario = st.text_input(label='Nombre', placeholder="Escribe un nombre al que dirigirnos")
            email = st.text_input(label='Email', placeholder="Escribe un email con el que poder contactar")
            consentimiento = st.checkbox("Acepto los términos y condiciones de la plataforma KnowSphere")
            aceptar_boton = st.form_submit_button(label="¡Empezar!")

        if consentimiento and aceptar_boton:
            if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                st.session_state['inicio'] = True
                st.experimental_rerun()
            else:
                st.warning("Por favor, introduce un email válido.")


#SECCION CHATEAR
if seleccion_menu == "Chat":
    st.write(f"## Grado: {st.session_state.grado}")

    if 'history' in st.session_state:
        for i, chat in enumerate(st.session_state.history):
            st_message(**chat, key=str(i)) #unpacking


    pregunta = st.text_input("Pregunta lo que quieras")

    columna1,columna2 = st.columns([0.1,1])
    with columna1:
        if st.button(label = "Chatear", type = "primary"):
            chatbot(pregunta)
            st.experimental_rerun()
    with columna2:
        if st.button(label="Borrar historial", type = "primary"):
            st.session_state['history'] = []
            st.experimental_rerun()

st.write(st.session_state.resultado)      


