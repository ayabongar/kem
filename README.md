# Vumatel.Poc.Chatbot

## Requirements
Python 3.8.10

## Getting started
To instantiate the virtual environment run the following command. Kindly ensure that you have the correct python version when running this command.
```
> python -m venv .venv
```

Following this you can activate the virtual environment with the below command.
```
> .\.venv\Scripts\activate
```

Next we install all our dependencies with
```
> pip install -r requirements.txt
```

Now we can train our Rasa model. First ensure that you navigate to the `rasa` folder
```
> cd src\rasa
> rasa train
```
