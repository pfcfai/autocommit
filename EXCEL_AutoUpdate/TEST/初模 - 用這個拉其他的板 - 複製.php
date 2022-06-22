<!doctype html>
<html lang="zh-tw" class="h-100">
{% load static %}
  <head>
    <meRachel Chenta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="統一期貨-Deep Trade | 深度交易平台以視覺化呈現全球經濟的關鍵數據與事件研究，提供完整的市場概況分析。再以AI 模型萃取各類標的的技術面趨勢，輔助投資人解析市場動向，有效提高投資效率。">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">

    <title>統一期貨-Deep Trade | 深度交易</title><!-- 為每個頁面設定唯一的標題 -->

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
    <!-- google fonts -->
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family==Noto+Sans+TC&display=swap">
    <!-- fontawesome icon -->
    <script defer src="https://use.fontawesome.com/releases/v5.0.10/js/all.js" integrity="sha384-slN8GvtUJGnv6ca26v8EzVaR9DC58QEwsIk9q1QXdCU8Yu8ck/tL/5szYlBbqmS+" crossorigin="anonymous"></script>
    <!-- common CSS -->
    <link rel="stylesheet" type="text/css" href="{% static 'css/common.css' %}">
    <style>
/*CSS 貼這*/
      .highcharts-figure, .highcharts-data-table table {
        min-width: 310px; 
        max-width: 800px;
        margin: 1em auto;
      }

      .highcharts-data-table table {
        font-family: Verdana, sans-serif;
        border-collapse: collapse;
        border: 1px solid #EBEBEB;
        margin: 10px auto;
        text-align: center;
        width: 100%;
        max-width: 500px;
      }
      .highcharts-data-table caption {
        padding: 1em 0;
        font-size: 1.2em;
        color: #555;
      }
      .highcharts-data-table th {
        font-weight: 600;
        padding: 0.5em;
      }
      .highcharts-data-table td, .highcharts-data-table th, .highcharts-data-table caption {
        padding: 0.5em;
      }
      .highcharts-data-table thead tr, .highcharts-data-table tr:nth-child(even) {
        background: #f8f8f8;
      }
      .highcharts-data-table tr:hover {
        background: #f1f7ff;
      }
      /*CSS 貼這 end*/


    </style>
    
    <!-- highcharts -->
   <!-- HTML 貼這 -->
    <script src="https://code.highcharts.com/highcharts.js"></script>
    <script src="https://code.highcharts.com/modules/histogram-bellcurve.js"></script>
    <script src="https://code.highcharts.com/modules/exporting.js"></script>
    <script src="https://code.highcharts.com/modules/accessibility.js"></script>
      <!-- HTML 貼這 end -->
    <!-- highcharts結束 -->
  </head>
  
  <body class="d-flex flex-column h-100">
  <!-- 導覽列 -->
  {% include header %}
  <!-- 導覽列結束 -->


<div>
  <div style="margin-left:auto;margin-right:auto;"><img src="{% static 'img/home/banner-01.png' %}" width="100%"></div>
</div>

<main role="main" class="container">
<hr>
<header></header>

<!-- 商品熱力圖 -->
  <!-- HTML 貼這 -->
<figure class="highcharts-figure">
  <div id="container"></div>
  <p class="highcharts-description">
    Chart showing how Highcharts can automatically compute a histogram from
    source data. In this chart, the source data is also displayed as a
    scatter plot.
  </p>
</figure>
  <!-- HTML 貼這 end -->
<script type="text/javascript">
  /JS 貼這/
var data = [-1.78, 1.64, -2.73, -2.07, 2.24, 0.0, 1.42, -3.89, -0.71, -1.58, -2.84, -1.32, -0.51, -1.57, -1.01, 0.8, 0.38, 3.34, -0.21, -6.2, 3.93, -1.53, 1.12, -1.2, -1.63, -0.15, 0.67, -0.36, 0.0, -1.24, 1.24, 3.41, 0.19, -3.79, -0.1, -2.99, -0.42, -1.54, 0.0, -2.06, 1.52, -4.63, -3.7, -2.18, -4.63, 0.44, 1.98, -0.81, 3.82, 4.72, 3.59, -2.14, 3.22, 0.14, -2.47, -0.71, 4.02, -0.68, 3.36, -3.61, -0.08, -3.52, -1.61, 0.59, -2.15, 0.89];

Highcharts.chart('container', {
  title: {
    text: 'Highcharts Histogram'
  },

  xAxis: [{
    title: { text: 'Data1' },
    alignTicks: false
  }, {
    title: { text: 'Histogram1' },
    alignTicks: false,
    opposite: true
  }],

  yAxis: [{
    title: { text: 'Data2' }
  }, {
    title: { text: 'Histogram2' },
    opposite: true
  }],

  plotOptions: {
    histogram: {
      accessibility: {
        pointDescriptionFormatter: function (point) {
          var ix = point.index + 1,
            x1 = point.x.toFixed(3),
            x2 = point.x2.toFixed(3),
            val = point.y;
          return ix + '. ' + x1 + ' to ' + x2 + ', ' + val + '.';
        }
      }
    }
  },

  series: [{
    name: 'Histogram',
    type: 'histogram',
    xAxis: 1,
    yAxis: 1,
    baseSeries: 's1',
    zIndex: -1
  }, {
    name: 'Data',
    type: 'scatter',
    data: data,
    id: 's1',
    marker: {
      radius: 1.5
    }
  }]
});
  /JS 貼這 end/
</script>
<!-- 商品熱力圖結束 -->


<header></header>
  <!-- footer -->
{% include footer %}
  <!-- footer結束 -->
  
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-160598077-1"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());

gtag('config', 'UA-160598077-1');
</script>


<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
      <script>window.jQuery || document.write('<script src="https://getbootstrap.com/docs/4.3/assets/js/vendor/jquery-slim.min.js"><\/script>')</script><script src="https://getbootstrap.com/docs/4.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-xrRywqdh3PHs8keKZN+8zzc5TX0GRTLCcmivcbNJWm2rs5C8PRhcEn3czEjhAO9o" crossorigin="anonymous"></script>
    </body>
</html>
