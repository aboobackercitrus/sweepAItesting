import re
from flask import Flask
from flask_restful import Api, Resource, reqparse
import requests
from bs4 import BeautifulSoup
import pandas as pd
"""Modules importing"""


app = Flask(__name__)
api = Api(app)

class Users(Resource):
    """starting of class"""
   
    def get(self):
        """starting of function or method"""
        parser1=reqparse.RequestParser()
        parser1.add_argument('book_name', required=True)
        args1 = parser1.parse_args()
        Search_book=args1['book_name']
        main_page = requests.get("https://sunnah.com/muslim")
        soup = BeautifulSoup(main_page.content, "html.parser")
        hadees_book = soup.find_all('div',class_=["english english_book_name"])
        book_list=[]
        for book in hadees_book:
            BookText=book.text
            book_list.append(BookText)
        #print(book_list)
            book_lis=pd.DataFrame(book_list, columns=["Topic name"])
            book_lis=book_lis[book_lis["Topic name"]!='Introduction']
        #print(book_lis)
        #Search_book=input("Enter book name: ")
        coun=0
        for book in book_lis["Topic name"]:
            if Search_book == book:
                x=book_lis[book_lis["Topic name"]==book].index[0]
                coun+=1
        if coun==0:
            return {'message' : f"Search keyword is not matching with Hadith Books: {Search_book}"}, 200
        else:
            parser2=reqparse.RequestParser()
            parser2.add_argument('search_one_from_above_book')
            args2 = parser2.parse_args()
            key1=args2['search_one_from_above_book']
            parser3=reqparse.RequestParser()
            parser3.add_argument('search_two_from_above_book', required=False)
            args3 = parser3.parse_args()
            key2=args3['search_two_from_above_book']
            page = requests.get(f"https://sunnah.com/muslim/{x}")
            #page = requests.get("https://sunnah.com/muslim/1")
            soup = BeautifulSoup(page.content, "html.parser")
            hadees = soup.find_all('div',class_="english_hadith_full")
            hadees_No=soup.find_all('tr', '&nbsp'==True)
            for text in soup.find_all({"span",'a','b'}): 
                text.decompose()
            hadees_no=[]
            for number in hadees_No:
                num=number.text
                if "In-book reference" in num:
                    num= re.sub('\xa0:\xa0',":",num)
                    hadees_no.append(num)
            hadees_text=[]
            for hadith in hadees:
                hadit= re.sub('\n',"",hadith.text)
                hadees_text.append(hadit)
            data = pd.DataFrame(list(zip(hadees_no,hadees_text)), columns=["Hadith Reference","Hadith"])
#             key1=input("Enter keyword 1: ")
#             key2=input("Enter keyword 2: ")
            count=0
            resul=[]
            for hade in data["Hadith"]:
                match1 = re.findall(fr'{key1}', hade)
                match2 = re.findall(fr'{key2}', hade)
                if match1!=[] or match2!=[]:
                    result=data[data['Hadith']==hade]
                    result=result.to_dict('records')
                    resul.extend(result)
                    count=count+1
            if count==0:
                return {'message' : "Search keywords are not matching with Hadith"}, 200
            else:
                resul=pd.DataFrame(resul)
                resul=resul.to_dict('records')
                return  resul, 200


        """4 Quran Subjects Index to get surah and ayah"""
        parser=reqparse.RequestParser()
        parser.add_argument('quran_subject_index_name', required=True)
        args = parser.parse_args()
        keyword=args['quran_subject_index_name']
        keyword=keyword.lower()
        let=keyword[0]
        url=requests.get(f"https://www.alim.org/quran/subject-index/letter/{let}/")
        soup=BeautifulSoup(url.content, 'lxml')
        #print(soup)
        res=[]
        hadees = soup.find_all('div',class_='row subject-row')
        for div in soup.find_all("div", class_={"col-sm-10",'sub-subject-text'}): 
            div.decompose()
        for hadee in hadees:
            hadees_name1=hadee.find('div',class_='col-sm-12').text
            #print(hadees_name1)

            subject= re.findall(r'[A-Za-z , ( ) -]+', hadees_name1)
            #print(subject)
            surath = re.findall(r"[-+]?\d*\.\d+|\d+", hadees_name1)
            #print(surath)
            for y in range(len(surath)): 
                    x=surath[y].split(".")
                    #print(x)
                    #print(subject[0])
                    subject[0]=subject[0].lower()
                    data = {'subject_name':subject[0],'surath_number': x[0], 'ayah_number': x[1]}
                    res.append(data)
            #print(res)
        for x in range(2,13):
            url2=requests.get(f"https://www.alim.org/quran/subject-index/letter/{let}/page/{x}/")
            soup2=BeautifulSoup(url2.content, 'lxml')
            hadees = soup2.find_all('div',class_='row subject-row')
            for div in soup2.find_all("div", class_={"col-sm-10",'sub-subject-text'}): 
                div.decompose()
            for hadee in hadees:
                hadees_name1=hadee.find('div',class_='col-sm-12').text
                #print(hadees_name1)

                subject= re.findall(r'[A-Za-z , ( ) -]+', hadees_name1)
                #print(subject)
                subject[0]=subject[0].lower()
                surath = re.findall(r"[-+]?\d*\.\d+|\d+", hadees_name1)
                #print(surath)
                for y in range(len(surath)): 
                        x=surath[y].split(".")
                        #print(x)
                        data = {'subject_name':subject[0],'surath_number': x[0], 'ayah_number': x[1]}
                        res.append(data)
        #         print(res)
        data=pd.DataFrame(res)
        df=data[data['subject_name']==f'{keyword}']    
        df=pd.DataFrame(df)
        df = df[(df.duplicated(subset = None,keep = 'last'))==False]
        #print(df)
        result = df.empty
        #print(result)
        df = df.to_dict('records')
        if    result:
            return {'message' : "Check Entered Subject Index Keyword"}, 200
        else:
            return  df, 200


        """6 ayah search from Sunnah hadees"""

        main_page = requests.get("https://sunnah.com/muslim")
        soup = BeautifulSoup(main_page.content, "html.parser")
        hadees_book = soup.find_all('div',class_=["english english_book_name"])
        book_list=[]
        # Search_book=input()
        for book in hadees_book:
            book_list.append(book.text)
        book_list=pd.DataFrame(book_list, columns=["Topic name"])
        book_list=book_list[book_list["Topic name"]!='Introduction']
        for book in book_list["Topic name"]:
            if Search_book == book:
                x=book_list[book_list["Topic name"]==book].index[0]
                #print(x)

        count=0
        res=[]
        page = requests.get(f"https://sunnah.com/muslim/{x}")
        soup = BeautifulSoup(page.content, "html.parser")
        hadees = soup.find_all('span',class_="arabic_text_details arabic")
        for hadee in hadees:
            hadees_name1=hadee.find('a',href=True)
            if hadees_name1!=None:
                count=count+1
                hadees_name1=hadees_name1.text
                resu1={'Ayah':hadees_name1}
                res.append(resu1)
        if count == 0:
            return {'message' : "Check Whether Entered Quran Ayah Exit"}, 200
            #print("")
        #res
        data4=pd.DataFrame(res, columns=["Ayah"])

        q_ayah1=data4
        data5=q_ayah1["Ayah"].replace('[{\u200f*\n}]','',regex=True)
        data5=pd.DataFrame(data5)
        #print(data1)
        def duplic(df2):
            df2= df2[(df2.duplicated(subset = None,keep = 'first'))==False]
            df2=df2.reset_index(drop=True)
            return df2
        data5=duplic(data5)
        return data5, 200


        """7-8,9-10,11-12"""
        def two_key(keywor1,keywor2):
            df=pd.read_json('ayahs.json')
            #data3=pd.read_csv("Sahih_muslim_arabic_ayah.csv")
            data=[]

            arabic_diacritics = re.compile(""""

                                        ۖ    |
                                        ۚ    |
                                       ۥ     |
                                        ۢ    |
                                        ُۥ    |
                                        ۭ    |
                                        ٓ    |
                                        ۟    |
                                        ۖ    |
                                        ۗ    |
                                       ،    |
                                       ۦ     
                                    """, re.VERBOSE)

            def preprocess(text):

                tha="تَـٰ"
                THA="تا"
                salath="ٱلصَّلَوٰ"
                Salath="الصلا"
                na="نَـٰ"
                Na="نا"
                la="لْـَٔا"
                La="لآ"
                aa="عَـٰ"
                Aa="عا"
                ma="مَـٰ"
                Ma="ما"
                ralif="رَٰ"
                rAlif="را"
                Alif= "ا"

                #remove longation

                text = re.sub("ٱلْحَيَوٰةِ","الحياة",text)
                text = re.sub("فِطْرَةَ ا","فطرت ا",text)
                text = re.sub("السَّلَمَ لَ","السلام ل",text)
                text = re.sub("السَّمَوَا","السماوا",text)
                text = re.sub("بِمُسَيْطِرٍ","بمصيطر",text)
                text = re.sub("ٱلرَّحْمَـٰنِ", "الرحمن", text)
                text = re.sub(salath,Salath,text)
                text = re.sub("كَـٰ",'كا',text)
                text = re.sub("وَٰ","وا",text)
                text = re.sub("صَـٰ",Alif, text)
                text = re.sub(ralif, rAlif, text)
                text = re.sub("ءَأَ", "اا", text)
                text = re.sub(ma,Ma,text)
                text = re.sub(aa,Aa,text)
                text = re.sub(la,La,text)
                text = re.sub("يَـٰ","يا" ,text)
                text = re.sub("يَّـٰ","يا" ,text)
                text = re.sub("ءَا", "ا", text)
                text = re.sub(tha,THA ,text)
                text = re.sub(na,Na,text)
                text = re.sub("حَـٰ","حا",text)
                text = re.sub("لَـٰ","لا",text)

                #print(text)
                text = re.sub( arabic_diacritics, '', text)
                text = re.sub('\s+','',text)
                return text


            #Step 0
            keywor1=preprocess(keywor1)
            keywor2=preprocess(keywor2)

            #STEP 1 Normalize
            from camel_tools.utils.normalize import normalize_unicode
            keywor1=normalize_unicode(keywor1)
            keywor2=normalize_unicode(keywor2)
            df['ayah_text']=df['ayah_text'].apply(normalize_unicode)

            #STEP 2: Reducing Orthographic Ambiguity
            from camel_tools.utils.normalize import normalize_alef_maksura_ar
            from camel_tools.utils.normalize import normalize_alef_ar
            from camel_tools.utils.normalize import normalize_teh_marbuta_ar

            def ortho_normalize(text):
                text = normalize_alef_maksura_ar(text)
                text = normalize_alef_ar(text)
                text = normalize_teh_marbuta_ar(text)
                return text

            keywor1 = ortho_normalize(keywor1)
            keywor2 = ortho_normalize(keywor2)
            df['ayah_text']=df['ayah_text'].apply(ortho_normalize)

            # STEP 3: Dediacritization
            from camel_tools.utils.dediac import dediac_ar
            keywor1 = dediac_ar(keywor1)
            keywor2 = dediac_ar(keywor2)
            df['ayah_text']=df['ayah_text'].apply(dediac_ar)



            coun=0
            for j in df['ayah_text']:
                match1 = re.findall(fr"{keywor1}", j)
                match2 = re.findall(fr"{keywor2}", j)
                #print(result)
                if match1!=[] or match2!=[]:
                    r=df.loc[df['ayah_text'] == j, ['surahNo','ayahNo']]
                    #print(r)
                    occu=r.shape[0]
                    if occu>1:
                        for i in range(occu): 
                            resul=r.iloc[i]
                            resul=df.loc[df['ayah_text'] == j, ['surahNo','ayahNo']].iloc[i]
                            #print(resul)
                            res={'SurahNo':resul[0],'AyahNo':resul[1]}
                            data.append(res)
                    else:
                        resul=df.loc[df['ayah_text'] == j, ['surahNo','ayahNo']].iloc[0]
                        res={'SurahNo':resul[0],'AyahNo':resul[1]}
                        #print(resul)
                        data.append(res)
                    coun=coun+1
            #print(coun)


            data=pd.DataFrame(data)
            data = data[(data.duplicated(subset = None,keep = 'first'))==False]
            if data.empty:
                return {'message' : "There is no Quranic Surah and Ayah based on this keywords or we need to upgrade our engine"}, 200
            else:
                data=data.sort_values(by='SurahNo')
                data = data.to_dict('records')
            return data, 200
        
        parser4=reqparse.RequestParser()
        parser4.add_argument('search_keyword_one_from_quran')
        args4 = parser4.parse_args()
        data6=args4['search_keyword_one_from_quran']
        parser5=reqparse.RequestParser()
        parser5.add_argument('search_keyword_two_from_quran', required=False)
        args5 = parser5.parse_args()
        data7=args5['search_keyword_two_from_quran']
        
        data6=two_key(data6,data7)
        
        parser6=reqparse.RequestParser()
        parser6.add_argument('search_keyword_one_from_quran')
        args6 = parser6.parse_args()
        data8=args6['search_keyword_one_from_quran']
        parser7=reqparse.RequestParser()
        parser7.add_argument('search_keyword_two_from_quran', required=False)
        args7 = parser7.parse_args()
        data9=args7['search_keyword_two_from_quran']
        
        data8=two_key(data8,data9)
        
        parser8=reqparse.RequestParser()
        parser8.add_argument('search_keyword_one_from_quran')
        args8 = parser8.parse_args()
        data10=args8['search_keyword_one_from_quran']
        parser9=reqparse.RequestParser()
        parser9.add_argument('search_keyword_two_from_quran', required=False)
        args9 = parser9.parse_args()
        data11=args9['search_keyword_two_from_quran']
        
        data10=two_key(data10,data11)
        
    # Add URL endpoints
api.add_resource(Users, '/')

if __name__ == '__main__':
    app.run()