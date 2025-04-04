from logger_config import logger

async def notes_prompt(transcript_text:str):
    prompt = """
        Your task is to convert the provided transcript into well-organized Markdown notes formatted for Jupyter notebooks. Please follow these guidelines to ensure clarity, accuracy, and consistency in rendering mathematical content:
 
        Headings:
        
        Use headings with varying numbers of # symbols to denote different heading levels.
        Inline Math:
        
        Use single dollar signs $ for inline math expressions. Example: $e^{i\pi} + 1 = 0$.
        Display Math:
        
        Use double dollar signs $$ for display math expressions. Example: $$ e^{i\pi} + 1 = 0 $$.
        Uniform Syntax:
        
        Maintain uniform syntax throughout the response to ensure consistency and readability.
        Example:
        
        Here is an example of how a heading and math expression should look:
        # Heading 1
        ## Heading 2
        $ e^{i\pi} + 1 = 0 $
        $$ e^{i\pi} + 1 = 0 $$
        Please convert the following transcript accordingly:
        
        Transcript:
        """
    if transcript_text:
        try:
            notes_prompt = prompt + transcript_text
            logger.info("notes prompt generated sucessfully")
        except Exception as e:
            logger.error(f"Error procrssing transcript: {e}")
            raise
    return notes_prompt


async def summary_qa_prompt(transcript_text:str,num_questions:int):
    prompt = f"""
    As a teacher who tries to make sure that a student understands each and every topic.
    Identify the topics and subtopics in the text which was connverted from pdf.
    can you generate summary.
    Can you generate exactly {num_questions} questions from the identified topics and subtopics in provided transcript. So that student can prepar for the test.
   
    Remove all the preambles.
    Here is the transcript text.
    TEXT: {transcript_text}
   
    Validate the questions and the options, and make sure they are based on factually correct information.
    """
    format_prompt = """
    It is very important that the response is a json with following format:
        {"Summary": generated summary,
        "Questions":[
            {{"Question": "Question",
            "Options": ["option1", "option2", "option3", "option4"],
            "CorrectAnswer": 1}},
            {{"Question": "Question",
            "Options": ["option1", "option2", "option3", "option4"],
            "CorrectAnswer": 2}},
            .....]
        }  
    ###INSTRUCTIONS:
    1.Only four options for each question (option 1, option 2, option 3, option 4)
    2.Correct answers can only be 1, 2, 3 or 4
    (   1 = option1
        2 = option2
        3 = option3
        4 = option4 )
    3.Make sure the questions are based on factually correct information.
    4.Formulate the questions such that they have only one correct and clear option as the answer.
    5. don't mention such kind of thing responses "Here is the JSON-formatted response with a summary and 20 questions based on the transcript:"
    """
    if transcript_text:
        try:
            summary_qa_prompt = prompt + format_prompt
            logger.info("Summary, question and answer prompt generated sucessfully")
        except Exception as e:
            logger.error(f"Error procrssing transcript: {e}")
            raise
    
    return summary_qa_prompt
