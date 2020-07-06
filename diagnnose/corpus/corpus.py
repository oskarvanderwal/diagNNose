from typing import Any, Dict, List, Optional, Union

from torchtext.data import Dataset, Example, Field, Pipeline, RawField, TabularDataset
from torchtext.vocab import Vocab

from diagnnose.vocab.create import create_vocab


class Corpus(Dataset):
    def __init__(
        self,
        examples: List[Example],
        fields: Dict[str, Field],
        vocab_path: Optional[str] = None,
        notify_unk: bool = False,
        tokenize_columns: Optional[List[str]] = None,
        create_pos_tags: bool = False,
        labels_column: str = "labels",
    ) -> None:
        super().__init__(examples, fields)

        self.vocab: Vocab = Vocab({}, specials=[])

        if vocab_path is not None:
            tokenize_columns = tokenize_columns or ["sen"]
            for column in tokenize_columns:
                self.attach_vocab(vocab_path, column, notify_unk)

        if labels_column in self.fields:
            self.fields[labels_column].build_vocab(self)

        if create_pos_tags:
            self.create_pos_tags()

    @classmethod
    def create(
        cls,
        path: str,
        header: Optional[List[str]] = None,
        header_from_first_line: bool = False,
        to_lower: bool = False,
        sen_column: str = "sen",
        labels_column: str = "labels",
        sep: str = "\t",
        vocab_path: Optional[str] = None,
        notify_unk: bool = False,
        tokenize_columns: Optional[List[str]] = None,
        create_pos_tags: bool = False,
    ) -> "Corpus":
        assert sep in "\t,", "separator not recognized, should be either `\t` or `,`"

        with open(path, encoding="utf8") as f:
            if header_from_first_line:
                next(f)
            raw_corpus = [line.strip() for line in f]

        header = cls.create_header(
            header=header,
            header_from_first_line=header_from_first_line,
            corpus_path=path,
            sen_column=sen_column,
            labels_column=labels_column,
            sep=sep,
        )

        fields = cls.create_fields(
            header,
            to_lower=to_lower,
            sen_column=sen_column,
            labels_column=labels_column,
            tokenize_columns=tokenize_columns,
        )

        examples = [
            Example.fromlist(line.split(sep), fields.items()) for line in raw_corpus
        ]

        return cls(
            examples,
            fields,
            vocab_path=vocab_path,
            notify_unk=notify_unk,
            tokenize_columns=tokenize_columns,
            create_pos_tags=create_pos_tags,
            labels_column=labels_column,
        )

    @staticmethod
    def create_fields(
        header: List[str],
        to_lower: bool = False,
        sen_column: str = "sen",
        labels_column: str = "labels",
        tokenize_columns: Optional[List[str]] = None,
    ) -> Dict[str, Field]:
        tokenize_columns = tokenize_columns or []

        def preprocess_sen(s: str) -> Union[str, int]:
            return int(s) if s.isdigit() else s

        pipeline = Pipeline(convert_token=preprocess_sen)
        fields = {}

        for column in header:
            if column == sen_column or column in tokenize_columns:
                fields[column] = Field(
                    batch_first=True, include_lengths=True, lower=to_lower
                )
            elif column == labels_column:
                fields[column] = Field(
                    pad_token=None,
                    unk_token=None,
                    is_target=True,
                    preprocessing=pipeline,
                )
            else:
                fields[column] = RawField(preprocessing=pipeline)
                fields[column].is_target = False

        return fields

    @staticmethod
    def create_header(
        header: Optional[List[str]] = None,
        header_from_first_line: bool = False,
        corpus_path: Optional[str] = None,
        sen_column: str = "sen",
        labels_column: str = "labels",
        sep: str = "\t",
    ) -> List[str]:
        if header is None:
            if header_from_first_line:
                with open(corpus_path) as f:
                    header = next(f).strip().split(sep)
            elif corpus_path is not None:
                # Infer header from file structure
                with open(corpus_path) as f:
                    first_line = next(f).strip().split(sep)
                if len(first_line) == 2:
                    header = [sen_column, labels_column]
                else:
                    header = [sen_column]
            else:
                header = [sen_column]

        assert sen_column in header, "`sen` should be part of corpus_header!"

        return header

    def attach_vocab(
        self, vocab_path: str, sen_column: str = "sen", notify_unk: bool = False
    ) -> None:
        """ Creates a Vocab instance that is attached to the Corpus.

        Parameters
        ----------
        vocab_path : str
            Path to model vocabulary file, expected to contain
            one entry per line.
        sen_column : str, optional
            Column name of the corpus sentences. Defaults to `sen`.
        notify_unk : bool, optional
            Toggle to issue a user warning if a requested token is not
            present in the model vocabulary. Defaults to False.
        """
        vocab = create_vocab(vocab_path, notify_unk=notify_unk)

        self.fields[sen_column].vocab = Vocab({}, specials=[])
        self.fields[sen_column].vocab.stoi = vocab
        self.fields[sen_column].vocab.itos = list(vocab.keys())

        self.vocab = self.fields[sen_column].vocab

    def create_pos_tags(self):
        import nltk

        nltk.download("averaged_perceptron_tagger")

        self.fields["pos_tags"] = RawField()
        self.fields["pos_tags"].is_target = False

        print("Tagging corpus...")
        for item in self:
            item.pos_tags = [t[1] for t in nltk.pos_tag(item.sen)]
