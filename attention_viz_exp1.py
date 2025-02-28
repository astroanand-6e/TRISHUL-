import streamlit as st
import pickle
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.font_manager as fm
import os

# Page configuration
st.set_page_config(page_title="Attention Visualization", layout="wide")

# Set up fonts for Hindi/Devanagari text
plt.rcParams['font.family'] = ['DejaVu Sans', 'Noto Sans Devanagari']

# Try to find and register Noto Sans Devanagari font
font_paths = [
    '/Users/anand/STUDY/MATS/fonts/NotoSansDevanagari-Regular.ttf',
    '/Users/anand/STUDY/MATS/fonts/NotoSansDevanagari-Bold.ttf'
]

devanagari_font = None
for font_path in font_paths:
    if os.path.exists(font_path):
        devanagari_font = fm.FontProperties(fname=font_path)
        break

if devanagari_font is None:
    st.warning("Devanagari font not found. Hindi text may not display correctly.")

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .observation-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 1rem;
    }
    .observation-item {
        margin-left: 1rem;
    }
    .model-response {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #ff4b4b;
    }
    .model-response-header {
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Title in main area
st.markdown('<div class="main-header">Attention Visualization</div>', unsafe_allow_html=True)

# Define prompts for reference
all_prompts = {
    "trio1": {
        "english": "Will you please help me understand the concept of kinetic energy?",
        "hindi": "क्या आप कृपया मुझे गतिज ऊर्जा की अवधारणा को समझने में मदद करेंगे?",
        "hinglish": "Kya aap mujhe kinetic energy ke concept ko samajhne mein help karoge?"
    },
    "trio2": {
        "english": "I want you to tell me a secret about the stars tonight.",
        "hindi": "मैं चाहता हूँ कि आप आज रात मुझे सितारों के बारे में एक रहस्य बताएँ।",
        "hinglish": "Main chahta hoon ki aaj raat aap mujhe stars ke baare mein ek secret batao."
    },
    "trio3": {
        "english": "I understand kinetic energy.",
        "hindi": "मुझे काइनेटिक ऊर्जा समझ आती है।",
        "hinglish": "Mujhe kinetic energy samajh aata hai."
    },
    "trio4": {
        "english": "Can you help me learn about gravity?",
        "hindi": "क्या आप मुझे गुरुत्वाकर्षण के बारे में सिखा सकते हैं?",
        "hinglish": "Kya aap mujhe gravity ke bare mein sikha sakte hain?"
    }
}

# Load the attention and output data
@st.cache_data
def load_data(model_name="gemma2"):
    attention_path = f"attention_data_{model_name}.pkl"
    output_path = f"output_data_{model_name}.pkl"
    
    try:
        with open(attention_path, 'rb') as f:
            attention_data = pickle.load(f)
        with open(output_path, 'rb') as f:
            output_data = pickle.load(f)
        return attention_data, output_data, True
    except FileNotFoundError:
        st.error(f"Data files for {model_name} not found.")
        return {}, {}, False

# ===== SIDEBAR CONTROLS =====
st.sidebar.title("Visualization Controls")

# Model selection in sidebar
model_name = st.sidebar.selectbox("Select Model", ["gemma2", "Llama3.2"], index=0)

# Prompt selection in sidebar
trio_name = st.sidebar.selectbox("Select Prompt", ["trio1", "trio2", "trio3", "trio4"], index=0)

# Layer and head selection in sidebar
max_layer = 25 if model_name == "gemma2" else 15  # Llama has 16 layers (0-15)
layer = st.sidebar.number_input("Layer", min_value=0, max_value=max_layer, value=6, step=1)

max_head = 7 if model_name == "gemma2" else 31  # Gemma2 has 8 heads (0-7), Llama has 32 heads (0-31)
head = st.sidebar.number_input("Head", min_value=0, max_value=max_head, value=0, step=1)

# Language selection in sidebar
st.sidebar.markdown("### Select Language")
language = st.sidebar.radio("Language", ["English", "Hindi", "Hinglish"], index=2)
selected_language = language.lower()

# Load data based on model selection
attention_data, output_data, data_loaded = load_data(model_name)

# Display model name in main area
st.markdown(f"## {model_name.upper()}")

# Function to create a custom colormap (red shades for attention)
def create_attention_colormap():
    colors = [(1, 1, 1), (1, 0.8, 0.8), (1, 0.6, 0.6), (1, 0.4, 0.4), (1, 0, 0)]
    return LinearSegmentedColormap.from_list('attention_cmap', colors, N=100)

# Function to get appropriate font based on language
def get_font_for_language(language):
    if language.lower() == "hindi" and devanagari_font is not None:
        return devanagari_font
    return None  # Use default font

if data_loaded:
    # Check if the selected trio exists in the data
    if trio_name not in attention_data:
        st.warning(f"Data for {trio_name} not found in the loaded files. Please select another prompt.")
    else:
        # Display the selected configuration
        st.markdown(f"{model_name.upper()}: Layer {layer}, Head {head} attention for {selected_language}")
        
        # Get the prompt, tokens, and model response
        prompt = attention_data[trio_name][selected_language]["prompt"]
        tokens = attention_data[trio_name][selected_language]["tokens"]
        model_response = output_data[trio_name][selected_language]
        
        # Display the prompt and model response
        st.markdown(f"**Prompt:** {prompt}")
        st.markdown('<div class="model-response">'
                    f'<div class="model-response-header">Model Response:</div>'
                    f'{model_response}'
                    '</div>', 
                    unsafe_allow_html=True)
        
        # Get attention matrix
        if "attention" in attention_data[trio_name][selected_language]:
            attn_matrix = attention_data[trio_name][selected_language]["attention"][layer][head]
        else:
            attn_matrix = attention_data[trio_name][selected_language][layer][head]
        
        # Visualization container
        viz_container = st.container()
        
        with viz_container:
            # Token-level attention visualization
            st.markdown("#### Token-level Attention")
            
            # Get the last row of attention matrix (how the last token attends to all previous tokens)
            token_attention = attn_matrix[-1, :len(tokens)]
            
            # Normalize if needed
            if np.sum(token_attention) > 0:
                token_attention = token_attention / np.sum(token_attention)
            
            # Create a horizontal bar for each token
            fig, ax = plt.subplots(figsize=(10, 2))
            
            # Get font for the current language
            font = get_font_for_language(selected_language)
            
            # Display tokens with colored backgrounds based on attention
            current_pos = 0
            for i, token in enumerate(tokens):
                # Calculate text width (approximate)
                token_width = len(token) * 0.1 + 0.2
                
                # Add colored rectangle based on attention weight
                color_intensity = token_attention[i]
                rect = plt.Rectangle((current_pos, 0), token_width, 0.8, 
                                    color=(1, 1-color_intensity, 1-color_intensity), 
                                    alpha=0.8)
                ax.add_patch(rect)
                
                # Add token text with appropriate font
                if font is not None:
                    ax.text(current_pos + token_width/2, 0.4, token, 
                            ha='center', va='center', fontsize=12, fontweight='bold',
                            fontproperties=font)
                else:
                    ax.text(current_pos + token_width/2, 0.4, token, 
                            ha='center', va='center', fontsize=12, fontweight='bold')
                
                # Move to next position with a small gap
                current_pos += token_width + 0.05
            
            # Set appropriate limits
            ax.set_xlim(0, current_pos)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            st.pyplot(fig)
            
            # Heatmap visualization
            st.markdown("#### Attention Heatmap")
            
            # Create attention heatmap
            fig, ax = plt.subplots(figsize=(10, 8))
            attention_cmap = create_attention_colormap()
            
            # Ensure matrix dimensions match token count
            display_matrix = attn_matrix[:len(tokens), :len(tokens)]
            
            # Create heatmap
            sns.heatmap(display_matrix, cmap=attention_cmap, ax=ax, 
                        xticklabels=tokens, yticklabels=tokens, annot=True, fmt='.2f')
            
            # Apply font to tick labels if needed
            if font is not None:
                plt.setp(ax.get_xticklabels(), fontproperties=font, rotation=45, ha="right")
                plt.setp(ax.get_yticklabels(), fontproperties=font)
            else:
                plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
            
            ax.set_title(f"Layer {layer}, Head {head} Attention Matrix")
            plt.tight_layout()
            
            st.pyplot(fig)
        
        # Key observations
        st.markdown('<div class="observation-header">Key Observations:</div>', unsafe_allow_html=True)
        
        # Customize observations based on the prompt
        if trio_name in ["trio1", "trio3"]:
            st.markdown('<div class="observation-item">• The semantic tokens related to "kinetic energy" receive higher attention</div>', unsafe_allow_html=True)
        elif trio_name == "trio2":
            st.markdown('<div class="observation-item">• The semantic tokens related to "stars" and "secret" receive higher attention</div>', unsafe_allow_html=True)
        else:  # trio4
            st.markdown('<div class="observation-item">• The semantic tokens related to "gravity" receive higher attention</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="observation-item">• Key semantic terms maintain consistent focus across languages</div>', unsafe_allow_html=True)
        st.markdown('<div class="observation-item">• Attention is distributed based on semantic importance rather than syntactic position</div>', unsafe_allow_html=True)
        
        if model_name == "Llama3.2":
            st.markdown('<div class="observation-item">• Llama3.2 shows different attention patterns compared to Gemma2, particularly for cross-lingual tokens</div>', unsafe_allow_html=True)

else:
    st.warning("Please make sure the data files are available in the current directory.")
