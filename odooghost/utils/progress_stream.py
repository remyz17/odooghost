import re
import typing as t

from odooghost.exceptions import StreamOutputError

from .stream import json_stream


def write_to_stream(s: str, stream: t.IO):
    try:
        stream.write(s)
    except UnicodeEncodeError:
        encoding = getattr(stream, "encoding", "ascii")
        stream.write(s.encode(encoding, errors="replace").decode(encoding))


def stream_output(output: t.Any, stream: t.IO) -> str:
    is_terminal = hasattr(stream, "isatty") and stream.isatty()
    stream = stream
    lines = {}
    diff = 0

    for event in json_stream(output):
        yield event
        is_progress_event = "progress" in event or "progressDetail" in event

        if not is_progress_event:
            print_output_event(event, stream, is_terminal)
            stream.flush()
            continue

        if not is_terminal:
            continue

        # if it's a progress event and we have a terminal, then display the progress bars
        image_id = event.get("id")
        if not image_id:
            continue

        if image_id not in lines:
            lines[image_id] = len(lines)
            write_to_stream("\n", stream)

        diff = len(lines) - lines[image_id]

        # move cursor up `diff` rows
        write_to_stream("%c[%dA" % (27, diff), stream)

        print_output_event(event, stream, is_terminal)

        if "id" in event:
            # move cursor back down
            write_to_stream("%c[%dB" % (27, diff), stream)

        stream.flush()


def print_output_event(event: dict, stream: t.IO, is_terminal: bool) -> None:
    if "errorDetail" in event:
        raise StreamOutputError(event["errorDetail"]["message"])

    terminator = ""

    if is_terminal and "stream" not in event:
        # erase current line
        write_to_stream("%c[2K\r" % 27, stream)
        terminator = "\r"
    elif "progressDetail" in event:
        return

    if "time" in event:
        write_to_stream("[%s] " % event["time"], stream)

    if "id" in event:
        write_to_stream("%s: " % event["id"], stream)

    if "from" in event:
        write_to_stream("(from %s) " % event["from"], stream)

    status = event.get("status", "")

    if "progress" in event:
        write_to_stream("{} {}{}".format(status, event["progress"], terminator), stream)
    elif "progressDetail" in event:
        detail = event["progressDetail"]
        total = detail.get("total")
        if "current" in detail and total:
            percentage = float(detail["current"]) / float(total) * 100
            write_to_stream(
                "{} ({:.1f}%){}".format(status, percentage, terminator), stream
            )
        else:
            write_to_stream("{}{}".format(status, terminator), stream)
    elif "stream" in event:
        write_to_stream("{}{}".format(event["stream"], terminator), stream)
    else:
        write_to_stream("{}{}\n".format(status, terminator), stream)


def get_digest_from_pull(events: t.List[dict]) -> t.Optional[str]:
    digest = None
    for event in events:
        status = event.get("status")
        if not status or "Digest" not in status:
            continue
        else:
            digest = status.split(":", 1)[1].strip()
    return digest


def get_image_id_from_build(events: t.List[dict]) -> t.Optional[str]:
    image_id = None
    for event in events:
        if "stream" in event:
            match = re.search(
                r"Successfully built ([0-9a-f]+)", event.get("stream", "")
            )
            if match:
                image_id = match.group(1)
    return image_id


def read_status(event: dict) -> str:
    status = event["status"].lower()
    if "progressDetail" in event:
        detail = event["progressDetail"]
        if "current" in detail and "total" in detail:
            percentage = float(detail["current"]) / float(detail["total"])
            status = "{} ({:.1%})".format(status, percentage)
    return status
