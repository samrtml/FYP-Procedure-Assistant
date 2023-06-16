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
    - [hololens_sequence_advisory_bulldozer.py](hl2ss_modified/viewer/hololens_sequence_advisory_bulldozer.py): Deploys the bulldozer assembly/disassembly sequence onto the Hololens 2. 
    - [hololens_sequence_advisory_chess.py](hl2ss_modified/viewer/hololens_sequence_advisory_chess.py):Deploys the bulldozer assembly/disassembly sequence onto the Hololens 2. 

    (Note you must follow all the steps in the [README](hl2ss_modified/README.md) in the hl2ss_modified folder to deploy the sequence onto the Hololens 2)

- Webcam Deployment:
    - [webcam_sequence_advisory.py](webcam_sequence_advisory.py): Deploys the chess and bulldozer examples to your PC and connected webcam. Instructions on how to use this script are below. 

- Helper Scripts:
    - [generate_sequence.py](generate_sequence.py): Allows the user to generate sequences which can be followed in the advisory scripts. Instructions on how to use this script are below. 
    - [context_robustness_test.py](context_robustness_test.py): Evaluates the systems performance on context representation sequences.
    - [locational_robustness_test.py](locational_robustness_test.py): Evaluates the systems performance on locational representation sequences.

## Dependencies 
We use a common environment for the execution of our scripts. This environment can be created using the following command: 
```conda env create -f environment_procedure_analysis.yml``` and our exported environment can be found [environment_procedure_analysis.yml](environment_procedure_analysis.yml).

## Instructions for webcam_sequence_advisory.py

## Instructions for generate_sequence.py

To use generate a custom sequence you can either use the live webcam approach or simply upload a folder of images and a command list. 

## State Representations

The following is short summary of the state representations styles used in this project.

### Context Representation

The context representation captures all the classes and the number of instances of each class in the current frame. The following table shows an example of the context representation for the bulldozer assembly sequence.

| Class            | loose_wheel | fitted_wheel | wheel_slot | loose_blade | fitted_blade  | loose_cabin | cabin_slot | screws |
| ---------------- | ----------- | ------------ | ---------- | ----------- | ------------- | ----------- | ---------- | ------ | 
| No.Detected      | 2           | 0            | 2          | 1           | 0             | 1           | 1          | 3      |

### Locational Representation

The locational representation captures the location of each class in the current frame. The following table shows an example of the locational representation for chess.

| Region Index     | 1 | 2 | 3 | ...  | 62  | 63 | 64 | 
| ---------------- | - | - | - | ---- | --- | -- | -- |
| Class Detected   | white-rook | white-pawn | empty  | ...  | empty             | black-pawn          | black-rook         |

## Training - Datasets & Scripts

