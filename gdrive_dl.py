import argparse
import re
import requests
from bs4 import BeautifulSoup as bs

class DownloadError(Exception):
    """Custom Exception used to signal dowload errors"""
    pass


def save_file_from_response(res, file_name = None):
    """Saves a download HTTP response to a file

    Given a download response object and an optional file name, streams the
    response content to a file. The file name is obtained from the
    Content-Disposition header unless given as the file_name argument.
    """

    # Ensure this is a download response
    if 'Content-Disposition' not in res.headers:
        raise DownloadError('The response does not contain the necessary Content-Disposition header')

    if file_name:
        save_file_name = file_name
    else:
        # Get the file name from the Content-Disposition header if possible,
        # otherwise default to "download.dat"
        save_file_name = 'download.dat'
        match = re.search('filename="([^"]+)"', res.headers['Content-Disposition'])
        if match and len(match.groups()) > 0:
            save_file_name = match.groups()[0]

    print('Downloading to file %r...' % save_file_name)
    with open(save_file_name, 'wb') as f:

        # Iterate through all response chunks and write each to the file
        for chunk in res.iter_content(chunk_size=1024):
            print('.', end='', flush=True)
            f.write(chunk)

        print('')

    print('Download complete')


def download_file(url, file_name = None):
    """Downloads a file from a Google Drive shareable URL"""

    # Check URL format
    if not re.search('\/open\?', url):
        raise DownloadError('Incorrect URL format: does not contain /open path element')

    # Modify the URL to request a file download
    dl_url = re.sub('\/open\?', r'/uc?', url + r'&export=download')

    # Create a HTTP session: if the file is large then the subsequent download
    # request needs to have the cookies set in the original request
    with requests.Session() as sess:

        # Request the download URL: this could result in the actual download
        # response if the file is small or a virus scan warning page if the
        # file is large
        res_page = sess.get(dl_url, stream=True)

        # If the response is a download then the file is small and was scanned
        # for viruses by Google. In this case, simply stream the response to a
        # file.
        if 'Content-Disposition' in res_page.headers and re.search('^attachment', res_page.headers['Content-Disposition']):
            print('Got direct download response')
            save_file_from_response(res_page, file_name)

        # Otherwise, the file was too large for Google to scan. In this case,
        # display a warning and then parse the response HTML for the actual
        # download link. Then perform another request for this actual link and
        # stream the response to a file.
        else:
            print('WARNING: file cannot be scanned for viruses by Google! Download will continue but please scan for viruses manually after download.')

            # Parse the HTML response
            page_html = bs(res_page.content, 'html.parser')

            # Try to find the #uc-download-link element
            link_el = page_html.find('a', {'id': 'uc-download-link'})
            if not link_el:
                raise DownloadError('Result page does not contain a known download link')

            # Build a final URL for the download from the link element's href
            # attribute
            link_href = 'https://drive.google.com' + link_el['href']

            # Perform the request and save to a file
            res_dl = sess.get(link_href, stream=True)
            save_file_from_response(res_dl, file_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Downloads a file given a Google Drive shareable URL')
    parser.add_argument(
        '-o',
        type=str,
        dest='output_filename',
        metavar='filename',
        help='Output filename; if not given then the file will be given the same name as the file on Google Drive'
    )
    parser.add_argument(
        'url',
        type=str,
        help='Shareable URL of file to download'
    )
    args = parser.parse_args()

    try:
        download_file(args.url, args.output_filename)
    except DownloadError as ex:
        print('ERROR: unable to download file: %s' % ex)
