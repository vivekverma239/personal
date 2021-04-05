# import torch 
# import numpy as np
# import tensorflow as tf
# from transformers import BertForQuestionAnswering
# from transformers import BertTokenizer

# model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad2')
# tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad2')

# def answer_question(question, answer_text):
#     '''
#     Takes a `question` string and an `answer_text` string (which contains the
#     answer), and identifies the words within the `answer_text` that are the
#     answer. Prints them out.
#     '''
#     # ======== Tokenize ========
#     # Apply the tokenizer to the input text, treating them as a text-pair.
#     input = tokenizer(question, answer_text, return_tensors='pt')
#     print(input)
#     print(input['input_ids'].shape)

#     # Report how long the input sequence is.

#     start_scores, end_scores = model(**input) # The segment IDs to differentiate question from answer_text

#     # ======== Reconstruct Answer ========
#     # Find the tokens with the highest `start` and `end` scores.
#     answer_start = torch.argmax(start_scores)
#     answer_end = torch.argmax(end_scores)

#     # Get the string versions of the input tokens.
#     tokens = tokenizer.convert_ids_to_tokens(input['input_ids'])

#     # Start with the first token.
#     answer = tokens[answer_start]

#     # Select the remaining answer tokens and join them with whitespace.
#     for i in range(answer_start + 1, answer_end + 1):
        
#         # If it's a subword token, then recombine it with the previous token.
#         if tokens[i][0:2] == '##':
#             answer += tokens[i][2:]
        
#         # Otherwise, add a space then the token.
#         else:
#             answer += ' ' + tokens[i]
#     return answer


# if __name__ == "__main__":
#     context = "<div>Leave Policy – India</div><div>Special Day Off</div><div>Employees will be eligible to 1 day holiday as Special Day Off. This is to enable the employee</div><div>to celebrate any special occasion. (The 1 day of special day off is included in the total holidays of 12 days mentioned above)</div><div>This can be taken once in a calendar year. A leave application has to be made to be able to avail this Special Day off. This is a self-approved leave. An employee needs to apply for this leave after discussion with immediate supervisor.</div><div>Eligibility:</div><div>Leave is accrued monthly @ 1.00 day per month. Entitlement of this leave will be prorated based on the employees’ date of joining in the Organization. Any new employee joining the organization on or before the 15th of the month will be eligible for that month’s holiday eligibility. Any new employee joining after the 15th the month will not be eligible for that month’s holiday eligibility. Hence an employee joining in the month of January on or before 15th will get 12 day of leave and an employee joining in the month of January after 15th will get 11 days of leave.</div><div>In case an employee exits the organization and he / she has availed excess leave over and above his / her monthly accrual, recovery will be done through full & final settlement for the excess leave taken over and above the accrued eligibility.</div><div>Leave Credit: The accrued leave will be credited to the employee as follows:</div><div>a.  Employees in the Role Band A: Quarterly credit in advance</div><div>b.  Employees in the Role Band B and above: Annual credit in advance</div><div>Accumulation: Public Holiday, Restricted Off and Special Day Off cannot be accumulated. Any unutilized leave balance will automatically lapse at the end of year on 31st December.</div><div>\n3.2.  Privilege Leave</div><div>Quantum: 21 working days per financial year.  (Excludes Weekly Offs, Public Holidays, Special Day, Restricted Holidays). The leave year runs from April 01 to March 31.</div><div>Accrual: Leave is accrued monthly @ 1.75 days per month. Any new employee joining after the 15th the month will not be eligible for that month’s eligibility. Hence an employee joining in the month of April on or before 15th will get 1.75 day’s eligibility and an employee joining in the month of April after 15th will not get any accrual for that month.</div><div>Leave Credit: The accrued leave will be credited to the employee as follows:</div><div>a.  Employees in the Role Band A: Quarterly credit in advance</div><div>b.  Employees in the Role Band B and above: Annual credit in advance</div><div>Permitted Accumulation: Privilege Leave balance accumulation cannot exceed 7 days as on March 31st of any financial year. The excess leaves shall automatically lapse.</div><div>In addition, employees will need to avail a minimum of 4 days of such carried forward Privilege Leave by September 30th of the financial year, and balance carried forward</div><div>Effective Date: March 01st, 2020 • Issue No 11 • Page 5 of 13 • Private & Non-Sensitive</div>"
#     answer = answer_question("what is the eligibility of special day off?",context)
#     print(answer)