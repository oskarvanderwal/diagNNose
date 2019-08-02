from argparse import ArgumentParser
from typing import Set, Tuple

from diagnnose.typedefs.config import ArgDescriptions


# TODO: consider adding default values here explicitly
def create_arg_descriptions() -> ArgDescriptions:
    arg_descriptions: ArgDescriptions = {
        "model": {
            "model_type": {
                "required": True,
                "help": "(required) Language model type, as of now either ForwardLSTM or GoogleLM.",
            }
        }
    }

    # Gulordava ForwardLSTM
    arg_descriptions["model"].update(
        {
            "state_dict": {
                "help": "Path to ForwardLSTM model parameters (pickled torch state_dict)"
            },
            "device": {
                "help": "(optional) Torch device name on which model will be run. Defaults to cpu."
            },
            "rnn_name": {
                "help": "(optional) Attribute name of rnn, defaults to `rnn`."
            },
            "encoder_name": {
                "help": "(optional) Attribute name of model encoder, defaults to `encoder`."
            },
            "decoder_name": {
                "help": "(optional) Attribute name of model decoder, defaults to `decoder`."
            },
        }
    )

    # GoogleLM
    arg_descriptions["model"].update(
        {
            "pbtxt_path": {
                "help": "Path to the .pbtxt file containing the GraphDef model setup."
            },
            "ckpt_dir": {
                "help": "Path to folder containing parameter checkpoint files."
            },
            "full_vocab_path": {
                "help": "Path to the full model vocabulary of 800k tokens. Note that `vocab_path` "
                "can be passed along as well, pointing toward the corpus that will be extracted. "
                "In that case only a subset of the model softmax will be loaded in."
            },
            "corpus_vocab_path": {
                "help": "(optional) Path to the corpus for which a vocabulary will be created. "
                "This allows for only a subset of the model softmax to be loaded in."
            },
            "create_decoder": {
                "help": "(optional) Toggle to load in the (partial) softmax weights. Can be set to "
                "false in case no decoding projection needs to be made, as is the case during "
                "activation extraction, for example."
            },
        }
    )

    arg_descriptions["init_states"] = {
        "init_states_pickle": {
            "help": "(optional) Path to pickle of the initial lstm states of the model. "
            "If no path is provided zero-initialized states will be used."
        },
        "init_states_corpus": {
            "help": "(optional) Path to corpus for which the final activation will be used as "
            "initial states to the model."
        },
        "save_init_states_to": {
            "help": "Path to which the newly computed init_states will be saved. "
            "If not provided these states won't be dumped."
        },
        "vocab_path": {
            "help": "Path to the model vocabulary, which should a file containing a vocab "
            "entry at each line."
        },
        "full_vocab_path": {
            "help": "Path to the full model vocabulary of 800k tokens. Note that `vocab_path` "
            "can be passed along as well, pointing toward the corpus that will be extracted. "
            "In that case only a subset of the model softmax will be loaded in."
        },
        "corpus_vocab_path": {
            "help": "(optional) Path to the corpus for which a vocabulary will be created. "
            "This allows for only a subset of the model softmax to be loaded in."
        },
    }

    arg_descriptions["corpus"] = {
        "corpus_path": {"required": True, "help": "(required) Path to a corpus file."},
        "corpus_header": {
            "nargs": "*",
            "help": "(optional) List of corpus attribute names. If not provided all lines will be "
            'considered to be sentences, with the attribute name "sen".',
        },
        "to_lower": {
            "type": bool,
            "help": "(optional) Convert corpus to lowercase, defaults to False.",
        },
        "header_from_first_line": {
            "type": bool,
            "help": "(optional) Use the first line of the corpus as the attribute  names of the "
            "corpus. Defaults to False.",
        },
    }

    arg_descriptions["vocab"] = {
        "vocab_path": {
            "help": "Path to the model vocabulary, which should a file containing a vocab "
            "entry at each line."
        }
    }

    arg_descriptions["activations"] = {
        # TODO: Provide explanation of activation names
        "activations_dir": {
            "help": "(required) Path to folder to which extracted embeddings will be written."
        }
    }

    arg_descriptions["extract"] = {
        "activation_names": {
            "required": True,
            "nargs": "*",
            "help": "(required) List of activation names to be extracted.",
        },
        "batch_size": {
            "type": int,
            "help": "(optional) Amount of sentences processed per forward step. "
            "Higher batch size increases extraction speed, but should "
            "be done accordingly to the amount of available RAM. Defaults to 1.",
        },
        "dynamic_dumping": {
            "type": bool,
            "help": "(optional) Set to true to directly dump activations to file. "
            "This way no activations are stored in RAM. Defaults to true.",
        },
        "create_avg_eos": {
            "type": bool,
            "help": "(optional) Set to true to directly store the average end of sentence "
            "activations. Defaults to False",
        },
        "only_dump_avg_eos": {
            "type": bool,
            "help": "(optional) Toggle to only dump the avg eos activation. Defaults to false.",
        },
        "cutoff": {
            "type": int,
            "help": "(optional) Stop extraction after n sentences. Defaults to -1 to extract "
            "entire corpus.",
        },
    }

    arg_descriptions["classify"] = {
        "activation_names": {
            "required": True,
            "nargs": "*",
            "help": "(required) List of activation names on which classifiers will be trained.",
        },
        "classifier_type": {
            "required": True,
            "help": "Classifier type, as of now only accepts `logreg`, but more will be added.",
        },
        "save_dir": {
            "required": True,
            "help": "(required) Directory to which trained models will be saved.",
        },
        "calc_class_weights": {
            "type": bool,
            "help": "(optional) Set to true to calculate the classifier class weights based on the "
            "corpus class frequencies. Defaults to false.",
        },
    }

    arg_descriptions["train_dc"] = {
        "data_subset_size": {
            "type": int,
            "help": "(optional) Subset size of the amount of data points that will be used for "
            "training. Train/test split is performed afterwards. Defaults to the entire "
            "data set.",
        },
        "train_test_split": {
            "type": float,
            "help": "(optional) Ratio of the train/test split. Defaults to 0.9.",
        },
    }

    arg_descriptions["decompose"] = {
        "decomposer": {
            "help": "(required) Class name of decomposer constructor. As of now either "
            "CellDecomposer or ContextualDecomposer. Defaults to ContextualDecomposer."
        },
        "decompose_o": {
            "help": " Toggles decomposition of the output gate. Defaults to False."
        },
        "rel_interactions": {
            "help": " Indicates the interactions that are part of the relevant decomposition. "
            "Possible interactions are: rel-rel, rel-b and rel-irrel. Defaults to rel-rel, "
            "rel-irrel & rel-b."
        },
        "bias_bias_only_in_phrase": {
            "help": " Toggles whether the bias-bias interaction should only be added when inside "
            "the relevant phrase. Defaults to True, indicating that only bias-bias "
            "interactions inside the subphrase range are added to the relevant decomposition."
        },
        "only_source_rel": {
            "help": " Relates to rel-irrel interactions. If set to true, only irrel_gate-rel_"
            "source interactions will be added to rel, similar to LRP (Arras et al., 2017)."
        },
        "only_source_rel_b": {
            "help": " Relates to rel-b interactions. If set to true, only b-rel_source "
            "interactions will be added to rel, similar to LRP (Arras et al., 2017)."
        },
        "input_never_rel": {
            "help": " Never add the Wx input to the rel part, useful when only investigating "
            "the model biases. Defaults to False."
        },
        "init_states_rel": {
            "help": " Directly add the initial cell/hidden states to the relevant part. "
            "Defaults to False."
        },
        "use_extracted_activations": {
            "help": " Allows previously extracted activations to be used to avoid unnecessary "
            "recomputations of those activations. Defaults to True."
        },
        "only_return_dec": {
            "help": " Only returns the decomposed cell states of the top layer, without "
            "calculating the corresponding decoder scores. Defaults to False."
        },
    }

    arg_descriptions["downstream"] = {
        "task_activations": {
            "help": "(optional) Dictionary mapping task names to subtasks to directories to which "
            "the task embeddings have been extracted. If a task is not provided the "
            "activations will be created during the task."
        },
        "lakretz_path": {
            "help": "(optional) Path to directory containing the Lakretz datasets that can be "
            "found in the github repo. If not provided the Lakretz tasks will not be tested."
        },
        "lakretz_tasks": {
            "help": "(optional) The downstream Lakretz tasks that will be tested. If not provided "
            "this will default to the full set of conditions."
        },
        "marvin_path": {
            "help": "(optional) Path to directory containing the Marvin datasets that can be "
            "found in the github repo. If not provided the Marvin tasks will not be tested."
        },
        "marvin_tasks": {
            "help": "(optional) The downstream Marvin tasks that will be tested. If not provided "
            "this will default to the full set of conditions."
        },
        "print_results": {
            "help": "(optional) Toggle on to print task results directly. Defaults to True."
        },
    }

    return arg_descriptions


def create_arg_parser(arg_groups: Set[str]) -> Tuple[ArgumentParser, Set[str]]:
    parser = ArgumentParser()

    # create group to load config from a file
    from_config = parser.add_argument_group(
        "From config file", "Provide full experiment setup via config json file."
    )
    from_config.add_argument(
        "-c", "--config", help="Path to json file containing extraction config."
    )

    # create group to provide info via commandline arguments
    # Required args are not set to be required here as they can come from --config
    from_cmd = parser.add_argument_group(
        "From commandline",
        "Specify experiment setup via commandline arguments. "
        "Can be combined with the json config, in which case these"
        " cmd arguments overwrite the config args.",
    )

    arg_descriptions = create_arg_descriptions()

    required_args: Set[str] = set()
    parsed_args: Set[str] = set()

    for group in arg_groups:
        group_args = arg_descriptions[group]

        for arg, arg_config in group_args.items():
            if arg not in parsed_args:
                parsed_args.add(arg)
                from_cmd.add_argument(
                    f"--{arg}",
                    nargs=arg_config.get("nargs", None),
                    type=arg_config.get("type", str),
                    help=arg_config["help"],
                )

                if arg_config.get("required", False):
                    required_args.add(arg)

    return parser, required_args
