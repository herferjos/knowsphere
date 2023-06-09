#cargando los módulos y librerias necesarias
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


#definimos la funcion de chat
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

#SELECCION UNIVERSIDAD E INICIO DE SESIÓN
if seleccion_menu == "Inicio":

    st.write("## Iniciar Sesión")
    with st.form(key="formulario"):
        universidad = st.selectbox('Universidad',
                                    ('Universidad Autónoma de Madrid', 'Universidad Complutense de Madrid', 'Universidad de Málaga', 'Universidad Europea')
                                    )
        usuario = st.text_input(label='Usuario', placeholder="Escribe tu usuario")
        email = st.text_input(label='Email', placeholder="Escribe el email de la universidad")
        consentimiento = st.checkbox("Acepto los términos y condiciones de la plataforma KnowSphere")
        aceptar_boton = st.form_submit_button(label="¡Empezar!")

    if consentimiento and aceptar_boton:
        if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            st.session_state['inicio'] = True
            st.experimental_rerun()
        else:
            st.warning("Por favor, introduce un email válido.")
    
    if 'inicio' in st.session_state:
        st.success("¡Has iniciado sesión correctamente, usa la pestaña Chat para comenzar!")


#SECCION CHATEAR
if seleccion_menu == "Chat":
    if 'inicio' in st.session_state:
        
        #PERMITE SELECCIONAR LA ASIGNATURA DESEADA
        asignatura = st.selectbox(
            'Elige la asignatura',
            ('Genómica', 'Matemáticas', 'Derecho Internacional', 'Historia')
        )
        
        #PERMITE CAMBIAR DE ASIGNATURA. A SU VEZ LIMPIA EL HISTORIAL Y EL FICHERO PARA ENCONTRAR LA BASE DE DATOS
        if st.button(label = "Seleccionar", type = "primary"):
            if asignatura == "Genómica":
                st.session_state['persist_directory'] = 'apuntes/biologia'
                st.session_state['asignatura'] = "Genómica"
                st.session_state['history'] = []
                st.session_state['chat_history'] = []
                st.experimental_rerun()
            elif asignatura == "Derecho Internacional":
                st.session_state['persist_directory'] = 'apuntes/derecho_internacional'
                st.session_state['asignatura'] = "Derecho Internacional"
                st.session_state['history'] = []
                st.session_state['chat_history'] = []
                st.experimental_rerun()
            elif asignatura == "Historia":
                st.session_state['persist_directory'] = 'apuntes/historia'
                st.session_state['asignatura'] = "Historia"
                st.session_state['history'] = []
                st.session_state['chat_history'] = []
                st.experimental_rerun()
        
        #MUESTRA LA ASIGNATURA SELECCIONADA
        if 'asignatura' in st.session_state:
            st.write(f"## Asignatura: {st.session_state.asignatura}")
            
            #MUESTRA EL HISTORIAL DE CONVERSACIÓN
            if 'history' in st.session_state:
                for i, chat in enumerate(st.session_state.history):
                    st_message(**chat, key=str(i)) #unpacking

            #MUESTRA LA CAJA PARA EL INPUT DEL USUARIO
            pregunta = st.text_input("Pregunta lo que quieras")
            
            #PERMITE MANDAR LA REQUEST O BORRAR EL HISTORIAL
            columna1,columna2 = st.columns([0.1,1])
            with columna1:
                if st.button(label = "Chatear", type = "primary"):
                    chatbot(pregunta)
                    st.experimental_rerun()
            with columna2:
                if st.button(label="Borrar historial", type = "primary"):
                    st.session_state['history'] = []
                    st.session_state['chat_history'] = []
                    st.experimental_rerun()
    else:
        #DENIEGA EL ACCESO SI NO SE HA INICIADO SESIÓN
        st.markdown("<h3 style='text-align: center;'>⛔Acceso Denegado⛔</h3>", unsafe_allow_html=True)
        st.error("Debes Iniciar Sesión en la primera página para poder continuar...")
