import re
import json
import os


def parse_word_from_file(file_path: str, lang="zh"):
    cn_words = set()

    regex_map = {
        "zh": r"[\u4e00-\u9fff]+",
        "en": r"[a-zA-Z][a-zA-Z ]*[a-zA-Z]"
    }
    r = re.compile(regex_map[lang])

    with open(file_path, mode="r", encoding='utf-8') as f:
        for c, l in enumerate(f.readlines()):
            cn_words = cn_words | set(r.findall(l))
            print(c, len(cn_words))

    return cn_words

def generate_dict(cn_words: set, from_lang="zh", to_lang="en", chunk=20, exist_dict=dict()):
    cn_words = [ w for w in cn_words if w not in exist_dict ]
    if cn_words:
        import translators as ts
        print(f"New words : {len(cn_words)}")
        t_dict = exist_dict

        try:
            for i in range(0, len(cn_words), chunk):
                bulk_list = cn_words[i:i + chunk]
                bulk = ",".join(bulk_list)
                res = map(
                    lambda x: x.strip(),
                    ts.translate_text(bulk, from_language=from_lang, to_language=to_lang).split(",")
                )
                t_dict = t_dict | dict(zip(bulk_list, res))
        finally:
            return t_dict
    else:
        return exist_dict

def translate_file(file_path: str, cn_eng_dict: dict, to_lang: str):
    name, ext = os.path.splitext(file_path)
    file_content = ""

    with open(file_path, mode="r") as f:
        file_content = f.read()
        cnt = 1
        for k, v in cn_eng_dict.items():
            print(cnt, "/", len(cn_eng_dict))
            file_content = file_content.replace(k, v)
            cnt += 1
    
    dir_path = os.path.join(*list(os.path.split(file_path))[:-1])
    res_path = os.path.join(dir_path, f"{to_lang}{ext}")
    with open(res_path, mode="w", encoding="utf-8") as f:
        f.write(file_content)


def sort_dict(d: dict, key: any, reverse=False):
    return dict(sorted(list(d.items()), key=key, reverse=reverse))


def save_dict(file_path: str, t_dict: dict):
    with open(file_path, mode="w", encoding="utf-8") as f:
        f.write(json.dumps(t_dict, ensure_ascii=False))


def load_dict(file_path: str):
    with open(file_path, mode="r", encoding="utf-8") as f:
        unsorted = json.loads(f.read())
        return sort_dict(unsorted, key=lambda x: len(x[0]), reverse=True)

def main():
    cn_words_all = set()
    from_language = "en"
    to_language = "ko"
    dict_file = f"translator/dict/{from_language}_to_{to_language}.json"
    files = [
        f"data/global_region.csv.d/{from_language}.csv",
        f"data/ip.merge.txt.d/{from_language}.txt",
    ]

    if os.path.exists(dict_file):
        t_dict = load_dict(dict_file)
    else:
        t_dict = {}

    for file_path in files:
        cn_words_all = cn_words_all | parse_word_from_file(file_path, lang=from_language)
    
    t_dict = generate_dict(cn_words_all, from_lang=from_language, to_lang=to_language, exist_dict=t_dict)
    t_dict = sort_dict(t_dict, key=lambda x: len(x[0]), reverse=True)
    save_dict(dict_file, t_dict)

    for file_path in files:
        translate_file(file_path, t_dict, to_lang=to_language)


if __name__ == "__main__":
    main()
