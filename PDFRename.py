import os
from os.path import expanduser
import argparse
import tkinter.filedialog
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTContainer, LTTextLine

def get_objs(layout, results):
    if not isinstance(layout, LTContainer):
        return
    for obj in layout:
        if isinstance(obj, LTTextLine):
            results.append({'text': obj.get_text(), 'height': obj.height})
        get_objs(obj, results)


def get_title(path):
    with open(path, "rb") as f:
        parser = PDFParser(f)
        document = PDFDocument(parser)
        laparams = LAParams(all_texts=True)
        rsrcmgr = PDFResourceManager()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        page = next(PDFPage.create_pages(document)) #１ページ目
        interpreter.process_page(page)
        layout = device.get_result()
        results = []
        get_objs(layout, results)
    f.close()
    if results:
        title = max(results, key=lambda x:x.get('height'))
        return title.get('text').strip()
    raise OSError


def main(path):
    try:
        os.rename(path, "{}/{}.pdf".format(os.path.dirname(path), get_title(path)))
        print("Rename Success:{}".format(path))
    except OSError:
        print("Title Get ERROR:{}".format(get_title(path)))



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-D', '--dir', action='store_true', help='ディレクトリ選択')
    args = parser.parse_args()
    home = expanduser("~")
    iDir = os.path.abspath(os.path.dirname(home))
    if args.dir:
        dir_path = tkinter.filedialog.askdirectory(initialdir = iDir)
        print(dir_path)
        files = os.listdir(dir_path)
        file_paths = [f for f in files if os.path.isfile(os.path.join(dir_path, f))]
        pdf_paths = [f for f in file_paths if f.endswith('.pdf')]
        for pdf_path in pdf_paths:
            main("{}/{}".format(dir_path, pdf_path))
    else:
        fTyp = [("", "*")]
        path = tkinter.filedialog.askopenfilename(filetypes=fTyp, initialdir=iDir)
        main(path)
