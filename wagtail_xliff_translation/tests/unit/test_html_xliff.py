import pytest

pytestmark = pytest.mark.django_db


def test_flat_html(html_parser):
    html_parser.feed(
        "<a href='https://google.nl'>hello world</a>hoebakek<ol><li>item_1</li><li>item_2</li></ol>"
    )
    assert html_parser.content_list == [
        ("a", "hello world"),
        ("a", "hoebakek"),
        ("li", "item_1"),
        ("li", "item_2"),
    ]
    assert (
        html_parser.html
        == "<a href='https://google.nl'>{placeholder_0}</a>{placeholder_1}"
        "<ol><li>{placeholder_2}</li><li>{placeholder_3}</li></ol>"
    )
    assert (
        html_parser.encode_html()
        == "PGEgaHJlZj0naHR0cHM6Ly9nb29nbGUubmwnPntwbGFjZWhvbGRlcl8wfTwvYT57cGxhY2Vob2xkZXJfMX08b2w+"
        "PGxpPntwbGFjZWhvbGRlcl8yfTwvbGk+PGxpPntwbGFjZWhvbGRlcl8zfTwvbGk+PC9vbD4="
    )

    html_parser.reset()
    html = """
    <div class="rich-text">
        <h2>Header2</h2>
        <ul class="None">
            <li>List item 1</li>
            <li>List item 2
                <ul>
                    <li>Deeper item 1</li>
                    <li>
                        <br class="break" />
                        <br />
                        Item with double break</li>
                </ul>
            </li>
        </ul>
        <hr />
        <p>
            <b>Bold item after HR</b>
            <img src="test/123/image.jpg" />
        </p>
        <p>
            <a href="https://test.com" follow>Link item</a>
        </p>
    </div>
    """
    html_parser.feed(html)
    assert '<div class="rich-text">' in html_parser.html
    assert "</div>" in html_parser.html

    html_parser.encode_html()
    # Encoding the html returns a new html string and does not replace the other
    assert '<div class="rich-text">' in html_parser.html
    assert "</div>" in html_parser.html

    assert html_parser.html
    assert html_parser.content_list

    # There are 7 data items, so placeholder 0-6 need to be in the HTML
    assert "{placeholder_0}" in html_parser.html
    assert "{placeholder_6}" in html_parser.html

    html_parser.reset()

    assert not html_parser.html
    assert not html_parser.content_list


def test_handle_img_tag(html_parser, image_factory):
    image = image_factory()
    filename = image.file.name.split("/")[1].split(".")[0]
    html = f'<img alt="alt.jpg" class="richtext-image full-width" src="original_images/{filename}.width-800.jpg" height="192" width="192">'  # noqa
    html_parser.feed(html)
    assert (
        html_parser.html
        == "<embed alt='alt.jpg' embedtype='image' format='fullwidth' id='1'/>"
    )


def test_handle_iframe_tag(html_parser):
    html = "<iframe src='https://player.vimeo.com/video/104600643?app_id=122963'>"
    html_parser.feed(html)

    assert (
        html_parser.html
        == "<embed embedtype='media' url='https://vimeo.com/104600643'/>"
    )

    html_parser.reset()
    html = "<iframe src='https://www.youtube.com/embed/sWOUi0PVTXw?feature=oembed'>"
    html_parser.feed(html)

    assert (
        html_parser.html
        == "<embed embedtype='media' url='https://youtu.be/sWOUi0PVTXw'/>"
    )


def test_handle_anchor_tag(html_parser, page, document_factory):
    document = document_factory()
    html = f"""
    <a href='mailto:test@test.test'>
    <a href='tel:0612345678'>
    <a href='#test'>
    <a href='https://fourdigits.nl/en/'>
    <a href='/documents/{document.id}/document'>
    <a href='/{page.slug}/'>
    """
    html_parser.feed(html)

    assert (
        html_parser.html
        == f"<a href='mailto:test@test.test'><a href='tel:0612345678'><a href='#test'><a href='https://fourdigits.nl/en/'><a id='{document.id}' linktype='document'><a id='{page.id}' linktype='page'>"  # noqa
    )
