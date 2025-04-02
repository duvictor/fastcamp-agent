#!/usr/bin/env python
# src/latest_ai_development/main.py
import sys
from crew import LatestAiDevelopmentCrew

def run():
    """
        Run the crew.
     """

    inputs = {'topic': 'Viagem para o Piauí'}
    LatestAiDevelopmentCrew().crew().kickoff(inputs=inputs)