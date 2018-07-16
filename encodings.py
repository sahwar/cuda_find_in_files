﻿''' Data from Py-documentation (7.2.3. Standard Encodings)
    Arabic/Chinese/Japanese/Korean/... codepages are skipped
'''

# Codec         Aliases                 Languages/Purpose
ENCODINGS = [
 ['mbcs',       'ANSI, dbcs',           'Win only: Encode operand according to the ANSI codepage (CP_ACP)']
,['cp866',      '866, IBM866',          'Russian']
,['cp1251',     'windows-1251',         'Bulgarian, Byelorussian, Macedonian, Russian, Serbian']
,['ascii',      '646, us-ascii',        'English']
,['cp037',      'IBM037, IBM039',       'English']
,['cp424',      'EBCDIC-CP-HE, IBM424', 'Hebrew']
,['cp437',      '437, IBM437',          'English']
,['cp500',      'EBCDIC-CP-BE, EBCDIC-CP-CH, IBM500', 'Western Europe']
,['cp737',      '',                     'Greek']
,['cp775',      'IBM775',               'Baltic languages']
,['cp850',      '850, IBM850',          'Western Europe']
,['cp852',      '852, IBM852',          'Central and Eastern Europe']
,['cp855',      '855, IBM855',          'Bulgarian, Byelorussian, Macedonian, Russian, Serbian']
,['cp856',      '',                     'Hebrew']
,['cp857',      '857, IBM857',          'Turkish']
,['cp858',      '858, IBM858',          'Western Europe']
,['cp860',      '860, IBM860',          'Portuguese']
,['cp861',      '861, CP-IS, IBM861',   'Icelandic']
,['cp862',      '862, IBM862',          'Hebrew']
,['cp863',      '863, IBM863',          'Canadian']
,['cp865',      '865, IBM865',          'Danish, Norwegian']
,['cp869',      '869, CP-GR, IBM869',   'Greek']
,['cp875',      '',                     'Greek']
,['cp1026',     'ibm1026',              'Turkish']
,['cp1140',     'ibm1140',              'Western Europe']
,['cp1250',     'windows-1250',         'Central and Eastern Europe']
,['cp1252',     'windows-1252',         'Western Europe']
,['cp1253',     'windows-1253',         'Greek']
,['cp1254',     'windows-1254',         'Turkish']
,['cp1255',     'windows-1255',         'Hebrew']
,['cp1257',     'windows-1257',         'Baltic languages']
,['cp65001',    '',                     'Win only: Windows UTF-8 (CP_UTF8)']
,['latin_1',    'iso-8859-1, iso8859-1, 8859, cp819, latin, latin1, L1', 'West Europe']
,['iso8859_2',  'iso-8859-2, latin2, L2',   'Central and Eastern Europe']
,['iso8859_3',  'iso-8859-3, latin3, L3',   'Esperanto, Maltese']
,['iso8859_4',  'iso-8859-4, latin4, L4',   'Baltic languages']
,['iso8859_5',  'iso-8859-5, cyrillic',     'Bulgarian, Byelorussian, Macedonian, Russian, Serbian']
,['iso8859_7',  'iso-8859-7, greek, greek8','Greek']
,['iso8859_8',  'iso-8859-8, hebrew',       'Hebrew']
,['iso8859_9',  'iso-8859-9, latin5, L5',   'Turkish']
,['iso8859_10', 'iso-8859-10, latin6, L6',  'Nordic languages']
,['iso8859_13', 'iso-8859-13, latin7, L7',  'Baltic languages']
,['iso8859_14', 'iso-8859-14, latin8, L8',  'Celtic languages']
,['iso8859_15', 'iso-8859-15, latin9, L9',  'Western Europe']
,['iso8859_16', 'iso-8859-16, latin10, L10','South-Eastern Europe']
,['koi8_r',     '',                     'Russian']
,['koi8_u',     '',                     'Ukrainian']
,['mac_cyrillic','maccyrillic',         'Bulgarian, Byelorussian, Macedonian, Russian, Serbian']
,['mac_greek',  'macgreek',             'Greek']
,['mac_iceland','maciceland',           'Icelandic']
,['mac_latin2', 'maclatin2, maccentraleurope', 'Central and Eastern Europe']
,['mac_roman',  'macroman, macintosh',  'Western Europe']
,['mac_turkish','macturkish',           'Turkish']
,['ptcp154',    'csptcp154, pt154, cp154, cyrillic-asian', 'Kazakh']
,['utf_32',     'U32, utf32',           'all languages']
,['utf_32_be',  'UTF-32BE',             'all languages']
,['utf_32_le',  'UTF-32LE',             'all languages']
,['utf_16',     'U16, utf16',           'all languages']
,['utf_16_be',  'UTF-16BE',             'all languages']
,['utf_16_le',  'UTF-16LE',             'all languages']
,['utf_7',      'U7, unicode-1-1-utf-7','all languages']
,['utf_8',      'U8, UTF, utf8',        'all languages']
,['utf_8_sig',  '',                     'all languages']
]
def get_encoding_names():
#   return ['{}\t{}'.format(
#						codec[0]
#					 ,  ('({}) '.format(codec[1]) if codec[1]!='' else '')+codec[2]
#                    )  
#           for codec in ENCODINGS]
    return ['{}\t{}'.format(
						codec[0]+(' ({}) '.format(codec[1]) if codec[1]!='' else '')
					 ,  codec[2]
                     )  
            for codec in ENCODINGS]
   #def get_encoding_names