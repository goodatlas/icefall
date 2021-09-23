
import sentencepiece as spm
from pathlib import Path
from typing import Dict, List, Tuple


def main():

    # lang_dir = Path(
    #    "/home/users/lucasjo/kobert")
    #model_file = lang_dir / "kobert_news_wiki_ko_cased-1087f8699e.spiece"

    lang_dir = Path(
        "data/lang_bpe_5000")
    model_file = lang_dir / "bpe.model"

    sp = spm.SentencePieceProcessor()
    sp.load(str(model_file))

    print(sp.encode("우리 딸 이름은 조수아 입니다.", out_type=str))
    print(sp.EncodeAsPieces('나는 오늘 아침밥을 먹었다.'))
    print(sp.EncodeAsPieces('올해 20살 하고도 4개월차 입니다'))
    print(sp.EncodeAsIds('올해 20살 하고도 4개월차 입니다'))
    print(sp.unk_id())
    print(sp.bos_id())
    print(sp.eos_id())
    print(sp.pad_id())


if __name__ == "__main__":
    main()
