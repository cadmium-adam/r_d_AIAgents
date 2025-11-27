from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


# model
llm = ChatOpenAI(model="gpt-5-nano")


class Movie(BaseModel):
    """A movie with details."""

    title: str = Field(..., description="The title of the movie")
    year: int = Field(..., description="The year the movie was released")
    director: str = Field(..., description="The director of the movie")
    rating: float = Field(..., description="The movie's rating out of 10")


llm_with_structure = llm.with_structured_output(Movie)
response = llm_with_structure.invoke("Provide details about the movie Inception")
print(response)
