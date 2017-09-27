# NLP_course
Assignments from the NLP course.

Assigment 1.
The script assignment_1_1.py correspond to the first part of the first assignment:  
"Corpus processing: tokenization and word counting"  

To run a simple version without any pre-processing or filtering:  
``` shell
python assignment_1_1.py INPUTFILE.txt
```
To run the complete final version using all the features:
``` shell
python assignment_1_1.py INPUTFILE.txt -sw -p -n -fc -l -u
```

Expected output:  
  -Print on screen with all statisticall information required for the assignment.  
  -File containing all tokens and their frequencies.  
  -File containing all words and their frequencies.  
  -File containing all bigrams and their frequencies.  


For the multiword expression task no other option it's necessary besides -mwe:

To see available set of options:
``` shell
python assignment_1_1.py INPUTFILE.txt -mwe
```
Expected output:  
  -File containing all multiword expressions and their frequencies.

To see all available options:
``` shell
python assignment_1_1.py -h
```

Options:  
  -o OPTION.txt         Root name for all output files.  
  -sw                   After tokenizing the corpus. Remove all stop words present on the tokens.  
  -p                    After tokenizing the corpus. Remove all punctuation marks present on the tokens.  
  -n                    Preprocessing step: Turns all digits into its word representation.  
  -fc                   Preprocessing step: Remove CJK characters and keep ASCII printables.  
  -l                    Lemmatize and tokenize at the same time the corpus. No need to tokenize again.  
  -u                    Preprocessing step: Replace URLs into a word token.  
  -mwe                  Find multiword expressions on dataset.  

The script assignment_1_2.py provides a way to calculate accuracy for the output of our POS tagger of choice (Stanford's POS Tagger) on the provided corpus from twitter.  

Havin the output the POS tagger we run the script as follows:  
``` shell
python assignment_1_2.py EXPECTED_TAGS.txt GENERATED_TAGS.txt
```
