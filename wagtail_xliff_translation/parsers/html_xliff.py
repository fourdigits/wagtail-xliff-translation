from base64 import b64encode
from html.parser import HTMLParser

from django.core.serializers.base import SerializationError

from wagtail.core.models import Page
from wagtail.images import get_image_model

ImageModel = get_image_model()


class HtmlXliffParser(HTMLParser):
    """
    Class used to parse rich text so we can generate XLIFF. We create a content list,
    which is a list containing all the data elements of a richtext source which can later
    be translated. We generate an HTML string identical to the original HTML, however we
    replace the data with placeholders so we can replace these placeholders with the
    translated content. The HTML string is encoded to base64.

    Example of the generated HTML string:
    <div>
        <h2>{placeholder_0}</h2>
        <p>{placeholder_1}</p>
        <ul>
            <li>{placeholder_2}</li>
            <li>{placeholder_3}</li>
        </ul>
    </div>

    with the content:
        ['header2', 'paragraph', 'li-item1', 'li-item2']
    """

    # List of selfclosing tags which are available for the richtext editors
    self_closing_tags = ["img"]

    def __init__(self):
        super().__init__()
        self._content_list = []
        self._html = ""
        self._index = 0
        self._current_tag = ""

    @property
    def content_list(self):
        return self._content_list

    @property
    def html(self):
        return self._html

    def error(self, message):
        raise SerializationError(message)

    def handle_starttag(self, tag, attrs):
        """
        Method that handles starttags. It's needed to differ from standard
        tags (e.g. <div> or <p>) and anchor, image and iframe tags.
        Furthermore, for each tag it's possible to receive attributes
        belonging to those tags, so we need to set each attribute
        """
        self._current_tag = tag
        if tag == "a":
            self._html += self._handle_anchor_tag(attrs)
        elif tag == "img":
            self._html += self._handle_img_tag(attrs)
        elif tag == "iframe":
            self._html += self._handle_iframe_tag(attrs)
        elif attrs:
            self._html += f"<{str(tag)}"
            for key, value in attrs:
                if not value:
                    # When value is 'None', python leaves it empty but we sometimes need the value 'None'
                    value = "None"
                self._html += f' {key}="{value}"'
            self._html += self._close_tag(tag, False)
        else:
            self._html += self._close_tag(tag, True)

    def handle_startendtag(self, tag, attrs):
        self._current_tag = tag
        if attrs:
            self._html += f"<{str(tag)}"
            for key, value in attrs:
                if not value:
                    value = "None"
                self._html += f' {key}="{value}"'
            self._html += " />"
        self._html += f"<{str(tag)}/>"

    def handle_endtag(self, tag):
        if tag == "iframe":
            return
        self._html += f"</{str(tag)}>"

    def handle_data(self, data):
        """
        Move the data to the content list and add placeholders to the HTML string
        """
        if data.strip():
            self._content_list.append((self._current_tag, data))
            self._html += f"{{{'placeholder_'+str(self._index)}}}"
            self._index += 1

    def encode_html(self):
        """
        Encode the html to base64. We also remove the outer div tag because wagtails adds the richtext div themselves.
        """
        html_temp = self._html
        try:
            html_temp = html_temp.split('<div class="rich-text">')[1].rsplit(
                "</div>", 1
            )[0]
        except IndexError:
            pass
        return b64encode(html_temp.encode("utf-8")).decode("utf-8")

    def _close_tag(self, tag, full=False):
        if tag in self.self_closing_tags:
            if full:
                return f"<{str(tag)}>"
            else:
                return ">"
        else:
            if full:
                return f"<{str(tag)}>"
            else:
                return ">"

    def _handle_img_tag(self, attrs):
        """
        The way Wagtail saves images to the database is in a different format than image tags.
        So, we convert the image tag here to the desired format. The eventual database value looks
        like the following:
            <embed alt=\"image.jpg\" embedtype=\"image\" format=\"fullwidth\" id=\"1234\"/>
        """
        alt = ""
        image_format = ""
        image_id = 0
        for key, value in attrs:
            if key == "alt":
                alt = value
            if key == "class":
                image_format = value.split()[1].replace("-", "")
            if key == "src":
                filename, _, extension = value.split("/")[-1].split(".")
        image_id = ImageModel.objects.get(file__endswith=f"{filename}.{extension}").id
        return f"<embed alt='{alt}' embedtype='image' format='{image_format}' id='{image_id}'/>"

    def _handle_iframe_tag(self, attrs):
        """
        The way wagtail saves videos to the database is almost identical to the image method seen
        above here. Instead of embedtype image, it uses media and the only other attribute
        is the video url. Example:
            <embed embedtype=\"media\" url=\"https://vimeo.com/104600643\"/>
        """

        def _get_source_from_attrs(attrs):
            for key, value in attrs:
                if key == "src":
                    return value

        url = _get_source_from_attrs(attrs)
        video_url = ""
        video_id = url.split("?")[0].rsplit("/", 1)[1]
        if "vimeo" in url:
            # We need to get the video id from the url attribute and create a new URL.
            video_url = f"https://vimeo.com/{video_id}"
        elif "youtube" in url:
            # Not sure if youtube has been removed or not, but adding youtube videos seems impossible
            video_url = f"https://youtu.be/{video_id}"
        else:
            # Unclear what providers are supported or notself.
            # Full list https://github.com/wagtail/wagtail/blob/main/wagtail/embeds/oembed_providers.py
            return

        return f"<embed embedtype='media' url='{video_url}'/>"

    def _handle_anchor_tag(self, attrs):
        """
        There are 6 different anchor types which can occur in a richtext:
            Document link (/document/123/document)
            Internal link (/en/page/)
            External link (http://google.nl)
            Mail link (mailto:example@email.com)
            Telephone link (tel:0612345678)
            Anchor link (#anchor_link)
        The first two are important, because wagtail saves them with an id and a linktype.
        The last four can be returned as normal anchor links
        """
        href = attrs[0][1]
        if href.startswith("/documents"):
            # we need to obtain the id from the url ('/documents/1915/download_6')
            document_id = href.split("/")[2]
            return f"<a id='{document_id}' linktype='document'>"
        elif href.startswith("/"):
            # we get the slug from the url
            slug = href.split("/")[-2]
            page = Page.objects.get(slug=slug)
            return f"<a id='{page.id}' linktype='page'>"
        else:
            return f"<a href='{attrs[0][1]}'>"

    def reset(self):
        super().reset()
        self._content_list = []
        self._html = ""
        self._index = 0
