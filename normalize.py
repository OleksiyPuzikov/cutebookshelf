# wxbookshelf?

__table = {
    1040:'A'
  , 1041:'B'
  , 1042:'V'
  , 1043:'G'
  , 1044:'D'
  , 1045:'E'
  , 1025:'Yo'
  , 1046:'Zh'
  , 1047:'Z'
  , 1048:'I'
  , 1049:'Y'
  , 1050:'K'
  , 1051:'L'
  , 1052:'M'
  , 1053:'N'
  , 1054:'O'
  , 1055:'P'
  , 1056:'R'
  , 1057:'S'
  , 1058:'T'
  , 1059:'U'
  , 1060:'F'
  , 1061:'H'
  , 1062:'C'
  , 1063:'Ch'
  , 1064:'Sh'
  , 1065:'Tsh'
  , 1068:''
  , 1067:'Y'
  , 1066:''
  , 1069:'E'
  , 1070:'Yu'
  , 1071:'Ya'
  , 1072:'a'
  , 1073:'b'
  , 1074:'v'
  , 1075:'g'
  , 1076:'d'
  , 1077:'e'
  , 1105:'yo'
  , 1078:'zh'
  , 1079:'z'
  , 1080:'i'
  , 1081:'y'
  , 1082:'k'
  , 1083:'l'
  , 1084:'m'
  , 1085:'n'
  , 1086:'o'
  , 1087:'p'
  , 1088:'r'
  , 1089:'s'
  , 1090:'t'
  , 1091:'u'
  , 1092:'f'
  , 1093:'h'
  , 1094:'c'
  , 1095:'ch'
  , 1096:'sh'
  , 1097:'tsh'
  , 1100:''
  , 1099:'y'
  , 1098:''
  , 1101:'e'
  , 1102:'yu'
  , 1103:'ya'
}


def __encode(src):
    i = ord(src)
    if i < 127:
        return src
    repl = __table.get(i, None)
    return repl is None and '%04d' % i or repl

def translit(src):
    return ''.join(map(__encode, src))

if __name__ == "__main__":
    print translit(u"\u0430\u0442\u0441\u0440\u0430\u043b")
