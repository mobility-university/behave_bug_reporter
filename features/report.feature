Feature: Report

  Background:
    Given an innocent step in background

  Scenario: First scenario
    Given this steps outputs "hello"
    When this step fails
    Then not reached here
    # Then a bug.txt is created to demonstrate how a bug could be reported