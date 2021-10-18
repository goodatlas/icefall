# -*- coding: utf-8 -*-
#  mostly based on https://github.com/scarletcho/KoG2P 

'''
g2p.py
~~~~~~~~~~

This script converts Korean graphemes to romanized phones and then to pronunciation.

    (1) graph2phone: convert Korean graphemes to romanized phones
    (2) phone2prono: convert romanized phones to pronunciation
    (3) graph2phone: convert Korean graphemes to pronunciation

Usage:  $ python g2p.py '스물 여덟째 사람'
        (NB. Please check 'rulebook_path' before usage.)

Yejin Cho (scarletcho@gmail.com)
Jaegu Kang (jaekoo.jk@gmail.com)
Hyungwon Yang (hyung8758@gmail.com)
Yeonjung Hong (yvonne.yj.hong@gmail.com)

Created: 2016-08-11
Last updated: 2017-02-22 Yejin Cho

* Key updates made:
    - Executable in both Python 2 and 3.
    - G2P Performance test available ($ python g2p.py test)
    - G2P verbosity control available

'''

import datetime as dt
import re
import math
import sys
import optparse
import argparse

CHOSUNG_LIST =  [u'ㄱ', u'ㄲ', u'ㄴ', u'ㄷ', u'ㄸ', u'ㄹ', u'ㅁ', u'ㅂ', u'ㅃ', u'ㅅ',\
                 u'ㅆ', u'ㅇ', u'ㅈ', u'ㅉ', u'ㅊ', u'ㅋ', u'ㅌ', u'ㅍ', u'ㅎ']
JUNGSUNG_LIST = [u'ㅏ', u'ㅐ', u'ㅑ', u'ㅒ', u'ㅓ', u'ㅔ', u'ㅕ', u'ㅖ', u'ㅗ', u'ㅘ',\
                 u'ㅙ', u'ㅚ', u'ㅛ', u'ㅜ', u'ㅝ', u'ㅞ', u'ㅟ', u'ㅠ', u'ㅡ', u'ㅢ', u'ㅣ']
JONGSUNG_LIST = [u'_', u'ㄱ', u'ㄲ', u'ㄳ', u'ㄴ', u'ㄵ', u'ㄶ', u'ㄷ', u'ㄹ', u'ㄺ',\
                 u'ㄻ', u'ㄼ', u'ㄽ', u'ㄾ', u'ㄿ', u'ㅀ', u'ㅁ', u'ㅂ', u'ㅄ', u'ㅅ',\
                 u'ㅆ', u'ㅇ', u'ㅈ', u'ㅊ', u'ㅋ', u'ㅌ', u'ㅍ', u'ㅎ']

ONS = ['k0', 'kk', 'nn', 't0', 'tt', 'rr', 'mm', 'p0', 'pp',
       's0', 'ss', 'oh', 'c0', 'cc', 'ch', 'kh', 'th', 'ph', 'h0']
NUC = ['aa', 'qq', 'ya', 'yq', 'vv', 'ee', 'yv', 'ye', 'oo', 'wa',
       'wq', 'wo', 'yo', 'uu', 'wv', 'we', 'wi', 'yu', 'xx', 'xi', 'ii']
COD = ['', 'kf', 'kk', 'ks', 'nf', 'nc', 'nh', 'tf',
       'll', 'lk', 'lm', 'lb', 'ls', 'lt', 'lp', 'lh',
       'mf', 'pf', 'ps', 's0', 'ss', 'oh', 'c0', 'ch',
       'kh', 'th', 'ph', 'h0']

EFF_COD = ['kf', 'nf', 'tf', 'll', 'mf', 'pf', 'ng']  # ㄱ ㄴ ㄷ ㄹ ㅁ ㅂ ㅇ

# Check Python version
ver_info = sys.version_info

if ver_info[0] == 2:
    reload(sys)
    sys.setdefaultencoding('utf-8')


def readfileUTF8(fname):
    f = open(fname, 'r')
    corpus = []

    while True:
        line = f.readline()
        line = line.encode("utf-8")
        line = re.sub(u'\n', u'', line)
        if line != u'':
            corpus.append(line)
        if not line: break

    f.close()
    return corpus


def writefile(body, fname):
    out = open(fname, 'w')
    for line in body:
        out.write('{}\n'.format(line))
    out.close()


def readRules(pver, rule_book):
    if pver == 2:
        f = open(rule_book, 'r')
    elif pver == 3:
        try:
            f = open(rule_book, 'r',encoding="utf-8")
        except Exception as e:
            return None, None
         
    rule_in = []
    rule_out = []

    while True:
        line = f.readline()
        if pver == 2:
            line = unicode(line.encode("utf-8"))
            line = re.sub(u'\n', u'', line)
        elif pver == 3:
            line = re.sub('\n', '', line)

        if line != u'':
            if line[0] != u'#':
                IOlist = line.split('\t')
                rule_in.append(IOlist[0])
                if IOlist[1]:
                    rule_out.append(IOlist[1])
                else:   # If output is empty (i.e. deletion rule)
                    rule_out.append(u'')
        if not line: break
    f.close()

    return rule_in, rule_out


def isHangul(charint):
    hangul_init = 44032
    hangul_fin = 55203
    return charint >= hangul_init and charint <= hangul_fin


def checkCharType(var_list):
    #  1: whitespace
    #  0: hangul
    # -1: non-hangul
    checked = []
    for i in range(len(var_list)):
        if var_list[i] == 32:   # whitespace
            checked.append(1)
        elif isHangul(var_list[i]): # Hangul character
            checked.append(0)
        else:   # Non-hangul character
            checked.append(-1)
    return checked


def graph2phone(graphs):
    # Encode graphemes as utf8
    try:
        graphs = graphs.decode('utf8')
    except AttributeError:
        pass

    integers = []
    for i in range(len(graphs)):
        integers.append(ord(graphs[i]))

    # Romanization (according to Korean Spontaneous Speech corpus; 성인자유발화코퍼스)
    phones = ''


    # Pronunciation
    idx = checkCharType(integers)
    iElement = 0
    while iElement < len(integers):
        if idx[iElement] == 0:  # not space characters
            base = 44032
            df = int(integers[iElement]) - base
            iONS = int(math.floor(df / 588)) + 1
            iNUC = int(math.floor((df % 588) / 28)) + 1
            iCOD = int((df % 588) % 28) + 1

            s1 = '-' + ONS[iONS - 1]  # onset
            s2 = NUC[iNUC - 1]  # nucleus

            if COD[iCOD - 1]:  # coda
                s3 = COD[iCOD - 1]
            else:
                s3 = ''
            tmp = s1 + s2 + s3
            phones = phones + tmp

        elif idx[iElement] == 1:  # space character
            tmp = '#'
            phones = phones + tmp

        phones = re.sub('-(oh)', '-', phones)
        iElement += 1
        tmp = ''

    # 초성 이응 삭제
    phones = re.sub('^oh', '', phones)
    phones = re.sub('-(oh)', '', phones)

    # 받침 이응 'ng'으로 처리 (Velar nasal in coda position)
    phones = re.sub('oh-', 'ng-', phones)
    phones = re.sub('oh([# ]|$)', 'ng', phones)

    # Remove all characters except Hangul and syllable delimiter (hyphen; '-')
    phones = re.sub('(\W+)\-', '\\1', phones)
    phones = re.sub('\W+$', '', phones)
    phones = re.sub('^\-', '', phones)
    return phones


def phone2prono(phones, rule_in, rule_out):
    # Apply g2p rules
    for pattern, replacement in zip(rule_in, rule_out):
        # print pattern
        phones = re.sub(pattern, replacement, phones)
        prono = phones
    return prono


def addPhoneBoundary(phones):
    # Add a comma (,) after every second alphabets to mark phone boundaries
    ipos = 0
    newphones = ''
    while ipos + 2 <= len(phones):
        if phones[ipos] == u'-':
            newphones = newphones + phones[ipos]
            ipos += 1
        elif phones[ipos] == u' ':
            ipos += 1
        elif phones[ipos] == u'#':
            newphones = newphones + phones[ipos]
            ipos += 1

        newphones = newphones + phones[ipos] + phones[ipos+1] + u','
        ipos += 2

    return newphones


def addSpace(phones):
    ipos = 0
    newphones = ''
    while ipos < len(phones):
        if ipos == 0:
            newphones = newphones + phones[ipos] + phones[ipos + 1]
        else:
            newphones = newphones + ' ' + phones[ipos] + phones[ipos + 1]
        ipos += 2

    return newphones




# represent pronunciation into Hangul format
def toGraphSeq(inProno):
    phones = inProno.split()

    # count 
    # 0 : onset
    # 1 : nucleus
    # 2 : coda
    count = 0
    han_prono = []
    for phone in phones:
        exp_count = count
        #print("> ##", exp_count, phone)

        # check if the phone is is onset, nucleus and coda
        if exp_count == 0 and phone not in ONS:
            count = 1
        if phone.startswith('-'):
            count = 0
            if phone.replace('-', '') not in ONS:
                count = 1
            phone = phone.replace('-', '')
        if exp_count == 2 and phone not in COD:
            if phone == 'ng': count = 2
            else:
                if phone in ONS: count = 0
                else: count = 1
        if exp_count == 2 and phone in COD and phone in ONS: count = 0  # it is onset

        if exp_count == 2 and count != exp_count:
            kor_graph = JONGSUNG_LIST[0]
            han_prono.append(kor_graph)
            #print("##", exp_count, '_', kor_graph)
            exp_count = 0                               # this is important

        if exp_count == 0 and count != exp_count:
            kor_graph = CHOSUNG_LIST[11]
            #print("##", exp_count, 'oh', kor_graph)
            han_prono.append(kor_graph)
        
        # convert the phone into Korean grapheme
        phone = phone.replace('-', '')
        if count == 0:
            kor_graph = CHOSUNG_LIST[ONS.index(phone)]
        elif count == 1:
            kor_graph = JUNGSUNG_LIST[NUC.index(phone)]
        else:
            if phone == 'ng':       # ng is not in the list
                kor_graph = u'ㅇ'
            else:
                if phone not in EFF_COD: print("WARNING: unappropriate coda {} is used")
                kor_graph = JONGSUNG_LIST[COD.index(phone)]

        han_prono.append(kor_graph)
        #print(count, phone, kor_graph)
    
        # loop
        if count == 2:
            count = 0
        else:
            count += 1

    # handle the last coda if it is needed
    if count == 2:
        kor_graph = JONGSUNG_LIST[0]
        han_prono.append(kor_graph)
        #print(count, '_', kor_graph)
       
    #print("###", han_prono)
    # 'ㅎ' 으로 끝나는 어절에대한 버그 수정
    if han_prono[-2] == "_" and han_prono[-1] == "ㅎ":
        han_prono[-2] = 'ㅅ'
        han_prono.pop(-1)
    outHangul = "".join(han_prono)
    return outHangul

def graph2prono(graphs, rule_in, rule_out, args=None):

    romanized = graph2phone(graphs)
    #print("### romanized: {}".format(romanized))
    romanized_bd = addPhoneBoundary(romanized)
    #print("### romanized_bd {}".format(romanized_bd))
    prono = phone2prono(romanized_bd, rule_in, rule_out)
    #print("### prono: {}".format(prono))

    prono = re.sub(u',', u' ', prono)
    prono = re.sub(u' $', u'', prono)
    prono = re.sub(u'#', u'-', prono)
    prono = re.sub(u'-+', u'-', prono)
    #print("### prono: {}".format(prono))

    prono_prev = prono
    identical = False
    loop_cnt = 1

    if args is None:
        verbose = False
    else:
        verbose = args.verbose

    #verbose = True

    if verbose == True:
        print ('=> Romanized: ' + romanized)
        print ('=> Romanized with boundaries: ' + romanized_bd)
        print ('=> Initial output: ' + prono)

    while not identical:
        prono_new = phone2prono(re.sub(u' ', u',', prono_prev + u','), rule_in, rule_out)
        prono_new = re.sub(u',', u' ', prono_new)
        prono_new = re.sub(u' $', u'', prono_new)
        #print("### prono_new: {}".format(prono_new))

        if re.sub(u'-', u'', prono_prev) == re.sub(u'-', u'', prono_new):
            identical = True
            #prono_new = re.sub(u'-', u'', prono_new)
            if verbose == True:
                print('\n=> Exhaustive rule application completed!')
                print('=> Total loop count: ' + str(loop_cnt))
                print('=> Output: ' + prono_new)
                print('=> Hangul: ' + toGraphSeq(prono_new))
        else:
            if verbose == True:
                print('\n=> Rule applied for more than once')
                print('cmp1: ' + re.sub(u'-', u'', prono_prev))
                print('cmp2: ' + re.sub(u'-', u'', prono_new))
            loop_cnt += 1
            prono_prev = prono_new
    return prono_new, toGraphSeq(prono_new)

def runKoG2P(graph, rulebook, args):
    [rule_in, rule_out] = readRules(ver_info[0], rulebook)
    if ver_info[0] == 2:
        prono, graph_seq = graph2prono(unicode(graph), rule_in, rule_out, args)
    elif ver_info[0] == 3:
        prono, graph_seq = graph2prono(graph, rule_in, rule_out, args)

    print(prono, graph_seq)

def g2p(args):
    if args.infile == sys.stdin:
        f = sys.stdin
    else:
        f = args.infile

    for line in f:
        tstr = line.strip()
        runKoG2P(tstr, 'rulebook.txt', args)

def main():
    parser = argparse.ArgumentParser(description='Korean grapheme-to-phone conversion')
    parser.add_argument('-v', action='store_true', dest='verbose', default='False',
            help="This option prints the detail information of g2p process.")
    parser.add_argument('infile', default=sys.stdin, type=argparse.FileType('r'), nargs='?')
    args = parser.parse_args()
    g2p(args)

if __name__ == '__main__':
    main()
