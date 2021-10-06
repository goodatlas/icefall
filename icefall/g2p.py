#!/usr/bin/env python3
# Author: Lucas Jo
# Data: 2017.07.23
# Ref.: https://www.korean.go.kr/front/page/pageView.do?page_id=P000097&mn_id=95
#
# This genPhoneSeq_fast.py generates Korean pronunciation with g2p.py
# mostly based on the ref. above. But a few rules are added to provide
# pronuncations when CODA 'ㅎ' + ONSET.
# In most case, I believe this will generate appropriate Korean pronunciation
# If is not, however, plz use genPhoneSeq.py. It generate prons without limit.
# The only downside of the scipts is it has dependency on konlpy and mecab
#
#
#  받침 대표음
#
#            ㄾ
#   ㄳ       ㄽ    ㅄ        ㅀ
#   ㄺ ㄵ    ㄾ ㄻ ㄿ        ㄶ
#   ----------------------------
#   ㄱ ㄴ ㄷ ㄹ ㅁ ㅂ ㅇ    (ㅎ)
#   ----------------------------
#   ㄲ    ㅅ       ㅍ
#   ㅋ    ㅆ
#         ㅈ
#         ㅊ
#         ㅌ
#
#
# 구현상 주의점
# 1.  15항 내용은 13항 앞서 적용함
#       맛없다 [마섭따] (x)
#              [마덥따] (o)


import re
import sys
import fileinput
from typing import List
from icefall._g2p import readRules, graph2prono
import argparse
from pathlib import Path

# Unicode
BASE_CODE = 0xac00  # 44032
START_CODE = 0x1100
MIDDLE_CODE = 0x1161
END_CODE = 0x11A7

CHOSUNG_LIST = [u'ㄱ', u'ㄲ', u'ㄴ', u'ㄷ', u'ㄸ', u'ㄹ', u'ㅁ', u'ㅂ', u'ㅃ', u'ㅅ',
                u'ㅆ', u'ㅇ', u'ㅈ', u'ㅉ', u'ㅊ', u'ㅋ', u'ㅌ', u'ㅍ', u'ㅎ']
JUNGSUNG_LIST = [u'ㅏ', u'ㅐ', u'ㅑ', u'ㅒ', u'ㅓ', u'ㅔ', u'ㅕ', u'ㅖ', u'ㅗ', u'ㅘ',
                 u'ㅙ', u'ㅚ', u'ㅛ', u'ㅜ', u'ㅝ', u'ㅞ', u'ㅟ', u'ㅠ', u'ㅡ', u'ㅢ', u'ㅣ']
JONGSUNG_LIST = [u'_', u'ㄱ', u'ㄲ', u'ㄳ', u'ㄴ', u'ㄵ', u'ㄶ', u'ㄷ', u'ㄹ', u'ㄺ',
                 u'ㄻ', u'ㄼ', u'ㄽ', u'ㄾ', u'ㄿ', u'ㅀ', u'ㅁ', u'ㅂ', u'ㅄ', u'ㅅ',
                 u'ㅆ', u'ㅇ', u'ㅈ', u'ㅊ', u'ㅋ', u'ㅌ', u'ㅍ', u'ㅎ']

CHOSUNG_SYM = [u'g', u'gg', u'n', u'd', u'dd', u'l', u'm', u'b', u'bb', u's',
               u'ss', u'', u'j', u'jj', u'ch', u'kh', u't', u'p', u'h']
JUNGSUNG_SYM = [u'a', u'ae', u'ya', u'yae', u'eo', u'e', u'yeo', u'ye', u'o', u'wa',
                u'wae', u'oe', u'yo', u'u', u'wo', u'we', u'wi', u'yu', u'eu', u'ui', u'i']
JONGSUNG_SYM = [u'', u'g2', u'', u'', u'n2', u'', u'', u'd2', u'l2', u'',
                u'', u'', u'', u'', u'', u'', u'm2', u'b2', u'', u'',
                u'', u'ng', u'', u'', u'', u'', u'', u'']

CHOSUNG_SYM_IPA = [u'k', u'k͈', u'n', u't', u't͈', u'ɾ', u'm', u'p', u'p͈', u'sʰ',
                   u's͈', u'', u't͡ɕ', u't͡ɕ͈', u't͡ɕʰ', u'kʰ', u'tʰ', u'pʰ', u'h']
JUNGSUNG_SYM_IPA = [u'a', u'ɛ', u'ja̠', u'jɛ̝', u'ʌ̹', u'e', u'jʌ', u'je', u'o', u'wa',
                    u'wɛ̝', u'we', u'jo', u'u', u'wʌ', u'we', u'y', u'ju', u'ɯ', u'ɰi', u'i']
JONGSUNG_SYM_IPA = [u'', u'k̚', u'', u'', u'n', u'', u'', u't̚', u'ɭ', u'',
                    u'', u'', u'', u'', u'', u'', u'm', u'p̚', u'', u'',
                    u'', u'ŋ', u'', u'', u'', u'', u'', u'']

# IPA (International Phonetic Alphabet) in Korean
#  http://www.ipachart.com
#  https://ko.wiktionary.org/wiki/위키낱말사전:국제_음성_기호 (IPA)
#  http://blog.daum.net/flowersym1970/87 (IPA)
#
#
# ㄱ  k   g   k
# ㄲ  k͈   k͈   k
# ㄴ  n   n   n
# ㄷ  t   d   t
# ㄸ  t͈   t͈
# ㄹ  ɾ   ɾ   ɭ
# ㅁ  m   m   m
# ㅂ  p   b   p
# ㅃ  p͈   p͈
# ㅅ  sʰ  sʰ  t
# ㅆ  s͈   s͈   t
# ㅇ          ŋ
# ㅈ  t͡ɕ  d͡ʑ  t
# ㅉ  t͡ɕ͈  t͡ɕ͈
# ㅊ  t͡ɕʰ t͡ɕʰ t
# ㅋ  kʰ  kʰ  k
# ㅌ  tʰ  tʰ  t
# ㅍ  pʰ  pʰ  p
# ㅎ  h   β   t
# ㅏ  a
# ㅑ  ja̠
# ㅓ  ʌ̹
# ㅕ  jʌ
# ㅗ  o
# ㅛ  jo
# ㅜ  u
# ㅠ  ju
# ㅡ  ɯ
# ㅣ  i
# ㅐ  ɛ
# ㅔ  e
# ㅒ  jɛ̝
# ㅖ  je
# ㅘ  wa
# ㅝ  wʌ
# ㅚ  we
# ㅟ  y
# ㅙ  wɛ̝
# ㅞ  we
# ㅢ  ɰi

# Ref.: http://blog.daum.net/_blog/BlogTypeView.do?blogid=06Se2&articleno=13296286
SYM_NOSOUND = '_'
DELIM_PRONUN = ':'


def toCode(idx, plist):
    if idx < 0 or idx >= len(plist):
        return SYM_NOSOUND
    else:
        return plist[idx]


def separate(ch):
    uindex = ord(ch) - 0xac00

    jongseong = uindex % 28
    joongseong = ((uindex - jongseong) // 28) % 21
    choseong = ((uindex - jongseong) // 28) // 21

    return [choseong, joongseong, jongseong]


def build(choseong, joongseong, jongseong):
    code = int(((((choseong) * 21) + joongseong) * 28) + jongseong + BASE_CODE)
    # try:
    #    # Python 2.x
    #    return unichr(code)
    # except NameError:
    # Python 3.x
    return chr(code)


def unroll(sentence):
    text = re.sub('[^ 가-힣]', '', sentence).strip()  # 띄어쓰기 남겨놓기
    # text = re.sub('[^가-힣]', '', sentence).strip()
    unrolled_indexes = []
    for i in range(len(text)):
        syllable = text[i]
        if syllable == u' ':
            unrolled_indexes.append([-1])
        else:
            indexes = separate(syllable)
            unrolled_indexes.append(indexes)
    return unrolled_indexes


def toPhonemeString(sentence):
    unrolled = unroll(sentence)

    oStr = ''
    for syllable in unrolled:
        if len(syllable) == 3:
            oStr += toCode(syllable[0], CHOSUNG_LIST)
            oStr += toCode(syllable[1], JUNGSUNG_LIST)
            oStr += toCode(syllable[2], JONGSUNG_LIST)
        else:
            oStr += '/'
    return oStr


def toUnrolled(pStr):

    text = re.sub('[/:]', '', pStr)
    if len(text) % 3 != 0:
        raise Exception(
            'Total length is not a multiple of 3: {}. {}'.format(len(text), text))
        # sys.exit('Total length is not a multiple of 3: {}. {}'.format(len(text), text))

    unrolled = []
    i = 0
    while i < len(pStr):
        if pStr[i] == '/' or pStr[i] == DELIM_PRONUN:
            unrolled.append([-1])
            i += 1
        else:
            start = CHOSUNG_LIST.index(pStr[i])
            middle = JUNGSUNG_LIST.index(pStr[i+1])
            end = JONGSUNG_LIST.index(pStr[i+2])
            unrolled.append([start, middle, end])
            i += 3

    return unrolled


def toHangul(pStr):

    unrolled = toUnrolled(pStr)

    outputText = ''
    for syllable in unrolled:
        if len(syllable) == 3:
            outputText += build(syllable[0], syllable[1], syllable[2])
        else:
            outputText += ' '

    return outputText


def pronun2psymbol(pronun, ipa=False):
    i = 0
    result = ''
    if pronun == '':
        return 'SIL'
    for syllable in pronun:
        if syllable == ' ':
            continue
        elif syllable == '+':
            result += ' + '
            continue

        sLoc = i % 3
        i += 1
        if ipa:
            if sLoc == 0:
                result += CHOSUNG_SYM_IPA[CHOSUNG_LIST.index(syllable)]+' '
            elif sLoc == 1:
                result += JUNGSUNG_SYM_IPA[JUNGSUNG_LIST.index(syllable)]+' '
            else:
                result += JONGSUNG_SYM_IPA[JONGSUNG_LIST.index(syllable)]+' '
        else:
            if sLoc == 0:
                result += CHOSUNG_SYM[CHOSUNG_LIST.index(syllable)]+' '
            elif sLoc == 1:
                result += JUNGSUNG_SYM[JUNGSUNG_LIST.index(syllable)]+' '
            else:
                result += JONGSUNG_SYM[JONGSUNG_LIST.index(syllable)]+' '

        result = re.sub('(\ )+', ' ', result)
    return result.strip()


def readRuleBook(g2p_dir):
    rulebook = g2p_dir / 'rulebook.txt'

    # read rule-book for Korean G2P
    ver_info = sys.version_info
    [rule_in, rule_out] = readRules(ver_info[0], rulebook)

    return rule_in, rule_out


def convert_text_to_phone_sequence(text: str) -> List[str]:

    g2p_dir = Path(__file__).parent
    [rule_in, rule_out] = readRuleBook(g2p_dir)

    phone_seq = []
    pronun_seq = []
    # do word-wise conversion
    for word in text.split():
        prono, graph_seq = graph2prono(word, rule_in, rule_out)
        phone_seq.extend(pronun2psymbol(graph_seq).split())
        pronun_seq.append(toHangul(graph_seq))

    return phone_seq, pronun_seq


def test():
    text = "뒤 에서 실탄 장전 한 사수 가 사람을 향해 총을 쏘기 시작했다 는 걸 알았 으니 정말 얼마나 놀랐 겠어"
    phone_seq, pronun_seq = convert_text_to_phone_sequence(text)
    print(f"input: {text}")
    print(f"output pronunciation: {' '.join(pronun_seq)}")
    print(f"output phone seq: {phone_seq}")


if __name__ == '__main__':
    test()
