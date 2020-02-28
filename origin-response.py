import boto3
from urllib.parse import unquote_plus
from urllib.parse import quote_plus

bucket = 's3bucketname'
s3 = boto3.resource('s3')
s3_bucket = s3.Bucket(bucket)

html_start = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>{TITLE}</title>
    <style type="text/css">
        a, a:active {text-decoration: none; color: blue;}
        a:visited {color: #48468F;}
        a:hover, a:focus {text-decoration: underline; color: red;}
        body {background-color: #F5F5F5;}
        h2 {margin-bottom: 12px;}
        table {margin-left: 12px;}
        th, td { font: 100% monospace; text-align: left;}
        th { font-weight: bold; padding-right: 14px; padding-bottom: 3px;}
        td {padding-right: 14px;}
        td.s, th.s {text-align: right;}
        div.list { background-color: white; border-top: 1px solid #646464; border-bottom: 1px solid #646464; padding-top: 10px; padding-bottom: 14px;}
        div.foot { font: 100% monospace; color: #787878; padding-top: 4px;}
    </style>
  </head>
  <body>
    <h2>{TITLE}</h2>
    <div class="list">
    <table summary="Directory Listing" cellpadding="0" cellspacing="0">
      <thead><tr><th class="n">Name</th><th class="m">Last modified</th><th class="s">Size</th></tr></thead>
      <tbody>
"""

html_end = """
      </tbody>
    </table>
    </div>
    <div class="foot"></div>
  </body>
</html>
"""

def lambda_handler(event, context):
    request = event["Records"][0]["cf"]["request"]
    response = event["Records"][0]["cf"]["response"]
    
    if request['uri'].endswith('/') or request['uri'] == '':
        prefix = unquote_plus(request['uri'][1:])
        
        title = 'Index of /' + prefix
        
        pre_dir = ''
        dir_pos = 1
        
        listing = [{
            'link': './',
            'name': './', 
            'last_modified': '&nbsp;', 
            'size': 0
        }]
        if prefix != '':
            listing.insert(1, {
                'link': '../',
                'name': '../', 
                'last_modified': '&nbsp;', 
                'size': 0
            })
            dir_pos += 1
        
        for object_summary in s3_bucket.objects.filter(Prefix=prefix):
            file_name = object_summary.key[len(prefix):]
            listing[0]['size'] += object_summary.size
                
            # current directory
            if file_name == '':
                listing[0]['last_modified'] = object_summary.last_modified
            
            # directory
            elif '/' in file_name:
                dir_name = file_name.split('/')[0] + '/'
                dir_path = './' + quote_plus(file_name.split('/')[0]) + '/'
                
                if pre_dir == dir_name:
                    listing[dir_pos-1]['size'] += object_summary.size
                    if listing[dir_pos-1]['last_modified'] < object_summary.last_modified:
                        listing[dir_pos-1]['last_modified'] = object_summary.last_modified
                else:
                    listing.insert(dir_pos, {
                        'link': dir_path,
                        'name': dir_name, 
                        'last_modified': object_summary.last_modified, 
                        'size': object_summary.size
                    })
                    dir_pos += 1
                    
                    pre_dir = dir_name
                    
            # file
            else:
                listing.append({
                    'link': './' + quote_plus(file_name),
                    'name': file_name, 
                    'last_modified': object_summary.last_modified, 
                    'size': object_summary.size
                })
                
        content = ''
        for row in listing:
            if isinstance(row['last_modified'], str):
                date_fmt = row['last_modified']
            else:
                date_fmt = row['last_modified'].strftime("%d.%m.%Y %H:%M:%S")
                
            content += """
      <tr>
        <td class="n"><a href='""" + row['link'] + """'>""" + row['name'] + """</a></td>
        <td class="m">""" + date_fmt + """</td>
        <td class="s">""" + sizeof_fmt(row['size']) + """</td>
      </tr>
"""
        
        response['status'] = '200'
        response['statusDescription'] = 'OK'
        response['headers']['content-type'] = [
                {
                    'key': 'Content-Type',
                    'value': 'text/html'
                }
            ]
        response['headers']['content-encoding'] = [
                {
                    'key': 'Content-Encoding',
                    'value': 'UTF-8'
                }
            ]
        response['body'] = html_start.replace('{TITLE}', title) + content + html_end
    
    return response

def sizeof_fmt(num, suffix='B'):
    for unit in ['&nbsp;','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Y', suffix)
