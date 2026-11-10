"""Converte a formatação de um DOCX para preto/branco sem alterar seu texto."""
import argparse
from pathlib import Path
from xml.dom import minidom
import zipfile

WORD = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
DRAWING = 'http://schemas.openxmlformats.org/drawingml/2006/main'
THEME_ATTRIBUTES = ('themeColor', 'themeTint', 'themeShade', 'themeFill', 'themeFillTint', 'themeFillShade')


def monochrome_xml(data):
    document = minidom.parseString(data)
    for node in document.getElementsByTagName('*'):
        for attribute in THEME_ATTRIBUTES:
            if node.hasAttributeNS(WORD, attribute):
                node.removeAttributeNS(WORD, attribute)
        if node.hasAttributeNS(WORD, 'color'):
            node.setAttributeNS(WORD, 'w:color', '000000')
        if node.namespaceURI == WORD:
            if node.localName == 'color':
                node.setAttributeNS(WORD, 'w:val', '000000')
            elif node.localName == 'shd':
                node.setAttributeNS(WORD, 'w:val', 'clear')
                node.setAttributeNS(WORD, 'w:fill', 'FFFFFF')
                node.setAttributeNS(WORD, 'w:color', '000000')
            elif node.localName == 'background':
                node.setAttributeNS(WORD, 'w:color', 'FFFFFF')
            elif node.localName == 'highlight':
                node.setAttributeNS(WORD, 'w:val', 'none')
        elif node.namespaceURI == DRAWING and node.localName == 'srgbClr':
            color = node.getAttribute('val').upper()
            node.setAttribute('val', 'FFFFFF' if color == 'FFFFFF' else '000000')
        elif node.namespaceURI == DRAWING and node.localName == 'sysClr':
            color = node.getAttribute('lastClr').upper()
            node.setAttribute('lastClr', 'FFFFFF' if color == 'FFFFFF' else '000000')
    return document.toxml(encoding='UTF-8')


def convert(source, target):
    if source.resolve() == target.resolve():
        raise ValueError('Escolha uma saída diferente para preservar o original.')
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source) as original, zipfile.ZipFile(target, 'w') as output:
        for entry in original.infolist():
            data = original.read(entry.filename)
            if entry.filename.endswith('.xml'):
                data = monochrome_xml(data)
            output.writestr(entry, data)
    with zipfile.ZipFile(target) as result:
        if result.testzip() is not None:
            raise ValueError('Não foi possível validar o DOCX.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('entrada', type=Path)
    parser.add_argument('saida', type=Path)
    args = parser.parse_args()
    convert(args.entrada, args.saida)
    print('Relatório Word formatado em preto e branco; conteúdo preservado.')


if __name__ == '__main__':
    main()
