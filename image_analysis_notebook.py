import streamlit as st
from snowflake.snowpark.context import get_active_session

# Initialize Snowflake session
session = get_active_session()

# Define app title and description
st.title("🖼️ Image Analysis with AI Models")
st.write("Analyze images using AI models via Snowflake Cortex")

# Sidebar for controls
with st.sidebar:
    st.header("Settings")
    
    # Model selection
    model = st.selectbox(
        "Select AI model",
        [
            "claude-3-5-sonnet",
            "pixtral-large"
        ],
        help="Choose which AI model to use for image analysis"
    )
    
    # Analysis type selection
    analysis_type = st.selectbox(
        "Select analysis type",
        [
            "Basic description",
            "Emotional analysis",
            "Object detection",
            "Text extraction",
            "Artistic elements",
            "Custom prompt"
        ]
    )
    
    # Custom prompt input
    if analysis_type == "Custom prompt":
        custom_prompt = st.text_area(
            "Enter your custom prompt",
            "Describe what you see in this image {0}.",
            help="Use {0} as a placeholder for the image"
        )

# Function to get image list
@st.cache_data(ttl=300)
def get_images():
    return session.sql("SELECT * FROM image_table").collect()

# Get the list of images
images = get_images()

# Image selector
image_paths = [row['IMAGE_PATH'] for row in images]
selected_image = st.selectbox("Select an image to analyze", image_paths)

# Display selected image
if selected_image:
    # Generate a presigned URL for the image
    image_url_result = session.sql(f"SELECT GET_PRESIGNED_URL('@image_analysis.images', '{selected_image}', 300)").collect()
    image_url = image_url_result[0][0]
    
    # Display the image
    st.image(image_url, caption=selected_image, use_container_width=True)
    
    # Analysis button
    if st.button("Analyze Image"):
        with st.spinner(f"AI model is analyzing the image..."):
            # Select the appropriate prompt based on analysis type
            if analysis_type == "Basic description":
                prompt = "Provide a brief description of the image {0}. 2-3 sentences maximum."
            elif analysis_type == "Emotional analysis":
                prompt = "Describe the emotions expressed by any people in the image {0}. If no people are present, state that."
            elif analysis_type == "Object detection":
                prompt = "List the main objects visible in the image {0}, ordered by prominence."
            elif analysis_type == "Text extraction":
                prompt = "Extract any visible text from the image {0}. If no text is present, state that."
            elif analysis_type == "Artistic elements":
                prompt = "Describe the artistic elements of this image {0} including colors, composition, lighting and style."
            else:
                prompt = custom_prompt
            
            # Run the analysis
            result = session.sql(f"""
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    '{model}', 
                    '{prompt}', TO_FILE('@images', '{selected_image}')
                )
            """).collect()[0][0]
            
            # Display result
            st.subheader("Analysis Result")
            st.write(result)