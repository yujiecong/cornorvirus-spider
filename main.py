"""
快捷键是command+j可以召唤出自带实用的模板
在你要打书签的位置，按下 Command + F11 ，你可以给这个位置加个序号，可以是数字也可以是字母，假如在下面这个位置 加了 1 这个序号，下次你就可以使用 Control + 1 直接跳转到这个位置。
点击 Run -> Profile '程序' ，即可进行性能分析。
我在搜索框输入 Error，就找到了快速定位到错误位置的快捷键 F2 和 Shift+F2 可以快速的定位到错误行。
Windows：按住Ctrl键，再按+或者- ）进行快速反折叠/折叠。"""
from pyecharts import options as opts
from pyecharts.charts import Page, Sankey
# V1 版本开始支持链式调用
# 你所看到的格式其实是 `black` 格式化以后的效果
# 可以执行 `pip install black` 下载使用
import requests
from pyecharts.render import make_snapshot
from pyecharts.charts import Map
from pyecharts.charts import Geo
from bs4 import BeautifulSoup
from snapshot_selenium import snapshot
def main(CITY):
    url='https://ncov.dxy.cn/ncovh5/view/pneumonia'
    CITY=CITY
    def get_ncov_data():
        ncov_soup=BeautifulSoup(requests.get(url=url).content.decode('utf8'),features='lxml')
        #去头去尾
        AreaStat=eval(str(ncov_soup.find('script',{'id':'getAreaStat'})).replace('<script id="getAreaStat">try { window.getAreaStat = ','').replace('}catch(e){}</script>','').replace('壮族自治区','').replace('维吾尔自治区','').replace('自治区','').replace('回族','').replace('省','').replace('市',''))
        return AreaStat
    ncov_data=get_ncov_data()
    def geo_heatmap() -> Map:
        c = (
            Map()
            .add(
                "全国疫情MAP",
                [list(z) for z in zip([city['provinceName'] for city in ncov_data],[city['confirmedCount'] for city in ncov_data])],

            )
            .set_series_opts(label_opts=opts.LabelOpts(is_show=True))
            .set_global_opts(
                visualmap_opts=opts.VisualMapOpts(),
                title_opts=opts.TitleOpts(title="MAP-HeatMap"),

            )
        )
        c.render()
        return c
    gd_data=[city['cities'] for city in ncov_data if city['provinceName']==CITY][0]
    def map_guangdong() -> Map:
        c = (
            Map()
            .add("{}nCoV分布".format(CITY),[list(z) for z in zip([c['cityName']+'市' for c in gd_data],[c['confirmedCount'] for c in gd_data])],CITY)
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Map-{}地图".format(CITY)),
                visualmap_opts=opts.VisualMapOpts(),
            )
        )
        c.render()
        return c
    with open('__china.geo.json', encoding='utf8')as f:
        data=eval(f.read())
    city_cp={}
    for ever in data['features']:
        if 'cp' not in ever['properties']:
            city_cp[ever['properties']['name']]=[ever['properties']['latitude'],ever['properties']['longitude']]
        else:
            city_cp[ever['properties']['name']]=ever['properties']['cp']

    def sankey_base() -> Sankey:
        cities_nodes = [
            {'name':'died'},
            {'name':'confirmed'},
            {'name':'suspected'},
            {"name":'cured'}
        ]
        for c in [city['provinceName'] for city in ncov_data]:
            cities_nodes.append({"name":c})
        confirmed_nodes=[city['confirmedCount'] for city in ncov_data]
        suspected_nodes=[city['suspectedCount'] for city in ncov_data]
        cured_nodes=[city['curedCount'] for city in ncov_data]
        links = [
        ]
        for i,cn in enumerate(confirmed_nodes):
            links.append({'source':ncov_data[i]['provinceName'],"target":'confirmed',"value":cn})
        #疑似
        for i, sn in enumerate(suspected_nodes):
            links.append({'source': ncov_data[i]['provinceName'], "target": 'suspected', "value": sn})
        for i, cn in enumerate(cured_nodes):
            links.append({'source': ncov_data[i]['provinceName'] ,"target": 'cured', "value": cn})
        c = (
            Sankey()
            .add(
                "nCoV-sankey",
                cities_nodes,
                links,
                linestyle_opt=opts.LineStyleOpts(opacity=0.2, curve=0.5, color="source"),
                label_opts=opts.LabelOpts(position="right"),
            )
            .set_global_opts(title_opts=opts.TitleOpts(title="Sankey-疫情图"))
        )
        c.render()
        return c
    map_guangdong()
    geo_heatmap()
    sankey_base()
    # make_snapshot(snapshot,map_guangdong().render(), "{}map.png".format(CITY))
    # make_snapshot(snapshot, geo_heatmap().render(), "cnmap.png")
    # make_snapshot(snapshot, sankey_base().render(), "cnsankey.png")
main()
