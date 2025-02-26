from typing import Any, Dict, List

from .operator import StreamInstanceOperator


class Tasker:
    pass


class FormTask(Tasker, StreamInstanceOperator):
    inputs: List[str]
    outputs: List[str]
    metrics: List[str]

    def process(self, instance: Dict[str, Any], stream_name: str = None) -> Dict[str, Any]:
        try:
            inputs = {key: instance[key] for key in self.inputs}
        except KeyError as e:
            raise KeyError(
                f"Unexpected input column names: {list(key for key in self.inputs if key not in instance)}"
                f"\n available names:{list(instance.keys())}\n given input names:{self.inputs}"
            )
        try:
            outputs = {key: instance[key] for key in self.outputs}
        except KeyError as e:
            raise KeyError(
                f"Unexpected output column names: {list(key for key in self.outputs if key not in instance)}"
                f" \n available names:{list(instance.keys())}\n given output names:{self.outputs}"
            )

        return {
            "inputs": inputs,
            "outputs": outputs,
            "metrics": self.metrics,
        }


class MultipleChoiceTask(FormTask):
    choices_field: str = "choices"
    choices_separator: str = "\n"
    enumeration_suffix: str = ". "
    use_text_in_target: bool = False
    alphabet: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def process_single_choice(self, choice: str, index: int, use_text: bool = True) -> str:
        try:
            processed_choice = f"{self.alphabet[index]}"
        except IndexError:
            raise ValueError(
                f"Too many choices, the length of alphabet '{self.alphabet}': {len(self.alphabet)} is the limit"
            )
        if use_text:
            processed_choice += f"{self.enumeration_suffix}{choice}"
        return processed_choice

    def process_choices(self, choices: List[str]) -> str:
        processed_choices = []
        for index, choice in enumerate(choices):
            processed_choices.append(self.process_single_choice(choice, index))
        return self.choices_separator.join(processed_choices)

    def process_target(self, choices, target_index):
        return self.process_single_choice(choices[target_index], target_index, use_text=self.use_text_in_target)

    def process(self, instance: Dict[str, Any], stream_name: str = None) -> Dict[str, Any]:
        result = super().process(instance, stream_name)
        target_key, target_value = next(iter(result["outputs"].items()))
        choices = result["inputs"][self.choices_field]
        target_index_in_choices = choices.index(target_value)

        processed_choices = self.process_choices(choices)
        processed_target = self.process_target(choices, target_index_in_choices)

        result["inputs"][self.choices_field] = processed_choices
        result["outputs"][target_key] = processed_target

        return result
