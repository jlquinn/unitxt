from src.unitxt.blocks import (
    LoadHF,
    SplitRandomMix,
    AddFields,
    SequentialRecipe,
    MapInstanceValues,
    FormTask,
    RenderFormatTemplate,
    InputOutputTemplate,
)

from src.unitxt.catalog import add_to_catalog
from src.unitxt.load import load_dataset
from src.unitxt.text_utils import print_dict

recipe = SequentialRecipe(
    steps=[
        LoadHF(
            path='glue',
            name='wnli',
        ),
        SplitRandomMix(
            mix={
                'train': 'train[95%]',
                'validation': 'train[5%]',
                'test': 'validation',
            }
        ),
        MapInstanceValues(
            mappers={
                'label': {"0": 'entailment', "1": 'not_entailment'}
            }
        ),
        AddFields(
            fields={
                'choices': ['entailment', 'not_entailment'],
            }
        ),
        FormTask(
            inputs=['choices', 'sentence1', 'sentence2'],
            outputs=['label'],
            metrics=['accuracy'],
        ),
        RenderFormatTemplate(
            template=InputOutputTemplate(
                input_format="""
                Given this sentence: {sentence1}, classify if this sentence: {sentence2} is {choices}.
                """.strip(),
                output_format='{label}',
            ),
        ),
    ]
)

add_to_catalog(recipe, 'wnli_fixed', collection='recipes', overwrite=True)

dataset = load_dataset('wnli_fixed')

print_dict(dataset['train'][0])