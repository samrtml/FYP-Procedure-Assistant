# FYP-Procedure-Assistant
This repository contains the implementation of my final year project procedure assistant, assisting is assembly/disassembly and chess. 


<p align="center">
    <img src="/showcase/bulldozer_disassemble.gif" width="640" height="360"/> 
</p>


## Repo Structure 
- analysis_library:
    - [context.py](analysis_library/context.py): Defines functions used for context representation analysis.
    - [locational.py](analysis_library/locational.py): Defines functions used for locational representation analysis.
    - [visual.py](analysis_library/visual.py): Defines functions used for visual display i.e draw bounding boxes and regions.
    - [packages.py](analysis_library/packages.py): Defines external imports and packages used.

- Hololens Deployment:
    - [hololens_sequence_advisory_bulldozer.py](hl2ss_modified/viewer/hololens_sequence_advisory_bulldozer.py): Deploys the bulldozer assembly/disassembly sequence onto the Hololens 2. (Note you must follow all the steps in the [README](hl2ss_modified/README.md) in the hl2ss_modified folder to deploy the sequence onto the Hololens 2)
    - [hololens_sequence_advisory_chess.py](hl2ss_modified/viewer/hololens_sequence_advisory_chess.py):Deploys the bulldozer assembly/disassembly sequence onto the Hololens 2. (Note you must follow all the steps in the [README](hl2ss_modified/README.md) in the hl2ss_modified folder to deploy the sequence onto the Hololens 2)

- Webcam Deployment:
    - [webcam_sequence_advisory.py](webcam_sequence_advisory.py): Deploys the chess and bulldozer examples to your PC and connected webcam. Instructions on how to use this script are below. 

- Helper Scripts:
    - [generate_sequence.py](generate_sequence.py): Allows the user to generate sequences which can be followed in the advisory scripts. Instructions on how to use this script are below. 
    - [context_robustness_test.py](context_robustness_test.py): Evaluates the systems performance on context representation sequences.
    - [locational_robustness_test.py](locational_robustness_test.py): Evaluates the systems performance on locational representation sequences.

## Instructions for generate_sequence.py

To use generate a custom sequence you can either use the live webcam approach or simply upload a folder of images and a command list. 

## Instructions for webcam_sequence_advisory.py
