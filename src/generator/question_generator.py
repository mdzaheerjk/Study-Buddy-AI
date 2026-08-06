from langchain_core.output_parsers import PydanticOutputParser
from src.models.question_schemsa import MCQQuestion,FillBlankQuestion
from src.prompts.templates import mcq_prompt_template,fill_blank_prompt_template
from src.llm.groq_client import get_groq_llm
from src.config.settings import settings
from src.common.logger import get_logger
from src.common.custom_exception import CustomException


class QuestionGenerator:
    def __init__(self):
        self.llm=get_groq_llm()
        self.logger=get_logger(self.__class__.__name__)

    def _retry_and_parse(self,prompt,parser,topic,difficulty):
        for attempt in range(settings.MAX_RETRIES):
            try:
                self.logger.info(f"Generating question for topic {topic} with difficulty{difficulty}")

                response=self.llm.invoke(prompt.fomat(topic=topic,difficulty=difficulty))

                parsed=parser.parse(response.content)

                self.logger.info("Sucesfully parsed the question")

                return parsed
            except Exception as e:
                self.logger.error(f"Error comming : {str(e)}")
                if attempt==settings.MAX_RETRIES-1:
                    raise CustomException(f"Generating Faield after {settings.MAX_RETRIES} attempts",e)

    def generate_mcq(self,topic:str,difficulty:str='medium')->MCQQuestion:
        try:
            parser=PydanticOutputParser(pydantic_object=MCQQuestion)

            question=self._retry_and_parse(mcq_prompt_template,parser,topic,difficulty)

            if len(question.options) !=4 or question.correct_answer not in question.options:
                raise ValueError("Invalid Mcq Structure")
            self.logger.info("Generated a Valid MCQ Question")
            return question
        except Exception as e:
            self.logger.error(f"Failed to Generate MCQ :{str(e)}")
            raise CustomException("MCQ generation Failed",e)

    def generate_fill_blank(self,topic:str,difficulty:str='medium')->FillBlankQuestion:
        try:
                parser=PydanticOutputParser(pydantic_object=FillBlankQuestion)

                question=self._retry_and_parse(fill_blank_prompt_template,parser,topic,difficulty)

                if "___" not in question.question:
                      raise ValueError("Fill in blanks should contain '___'")
                self.logger.info("Generated A valid Fill in Blanks Question") 
                return question
        except Exception as e:
            self.logger.error(f"Failed to Generate fillups : {str(e)}") 
            raise CustomException("Fill in blanks generation failed ",e)       

