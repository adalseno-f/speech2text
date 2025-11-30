#!/bin/bash
# Audio Splitter Script
# Splits long audio files into segments with optional overlap

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Default values
SEGMENT_LENGTH=1800  # 30 minutes in seconds
OVERLAP=30           # 30 seconds overlap
OUTPUT_FORMAT="mp3"

usage() {
    echo -e "${BLUE}Usage:${NC} $0 <input_file> [options]"
    echo ""
    echo "Options:"
    echo "  -l, --length <seconds>    Segment length in seconds (default: 1800 = 30 min)"
    echo "  -o, --overlap <seconds>   Overlap between segments in seconds (default: 30)"
    echo "  -f, --format <format>     Output format (default: mp3)"
    echo "  -d, --output-dir <dir>    Output directory (default: same as input)"
    echo "  -h, --help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 long_audio.mp3"
    echo "  $0 long_audio.mp3 -l 1200 -o 60"
    echo "  $0 recording.wav -f mp3 -d ./segments"
    echo ""
    exit 1
}

# Parse arguments
INPUT_FILE=""
OUTPUT_DIR=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -l|--length)
            SEGMENT_LENGTH="$2"
            shift 2
            ;;
        -o|--overlap)
            OVERLAP="$2"
            shift 2
            ;;
        -f|--format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        -d|--output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            if [ -z "$INPUT_FILE" ]; then
                INPUT_FILE="$1"
            else
                echo -e "${RED}Error: Unknown argument $1${NC}"
                usage
            fi
            shift
            ;;
    esac
done

# Check if input file is provided
if [ -z "$INPUT_FILE" ]; then
    echo -e "${RED}Error: Input file required${NC}"
    usage
fi

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo -e "${RED}Error: File not found: $INPUT_FILE${NC}"
    exit 1
fi

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${RED}Error: ffmpeg not found. Please install ffmpeg.${NC}"
    exit 1
fi

# Get file info
BASENAME=$(basename "$INPUT_FILE")
FILENAME="${BASENAME%.*}"
INPUT_DIR=$(dirname "$INPUT_FILE")

# Set output directory
if [ -z "$OUTPUT_DIR" ]; then
    OUTPUT_DIR="$INPUT_DIR"
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}Audio Splitter${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}Input file:${NC} $INPUT_FILE"
echo -e "${BLUE}Segment length:${NC} $SEGMENT_LENGTH seconds ($(($SEGMENT_LENGTH / 60)) minutes)"
echo -e "${BLUE}Overlap:${NC} $OVERLAP seconds"
echo -e "${BLUE}Output format:${NC} $OUTPUT_FORMAT"
echo -e "${BLUE}Output directory:${NC} $OUTPUT_DIR"
echo ""

# Get duration using ffprobe
echo -e "${BLUE}Getting audio duration...${NC}"
DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$INPUT_FILE")
DURATION_INT=$(awk "BEGIN {printf \"%.0f\", $DURATION}")
DURATION_MIN=$(awk "BEGIN {printf \"%.1f\", $DURATION/60}")

echo -e "${GREEN}Duration: $DURATION_MIN minutes ($DURATION_INT seconds)${NC}"

# Check if file needs splitting
if [ "$DURATION_INT" -le "$SEGMENT_LENGTH" ]; then
    echo -e "${YELLOW}File is shorter than segment length. No splitting needed.${NC}"
    exit 0
fi

# Calculate number of segments
# We need overlap, so segments will have some redundancy
SEGMENT_COUNT=$(awk "BEGIN {print int(($DURATION_INT - $OVERLAP) / ($SEGMENT_LENGTH - $OVERLAP)) + 1}")

echo -e "${BLUE}Will create $SEGMENT_COUNT segments${NC}"
echo ""

# Split the audio
for ((i=0; i<SEGMENT_COUNT; i++)); do
    # Calculate start time with overlap
    if [ $i -eq 0 ]; then
        START_TIME=0
    else
        START_TIME=$(awk "BEGIN {print ($i * ($SEGMENT_LENGTH - $OVERLAP))}")
    fi

    # Calculate duration for this segment
    if [ $i -eq $((SEGMENT_COUNT - 1)) ]; then
        # Last segment: take everything remaining
        SEGMENT_DURATION=$(awk "BEGIN {print ($DURATION_INT - $START_TIME)}")
    else
        SEGMENT_DURATION=$SEGMENT_LENGTH
    fi

    # Format times for display
    START_MIN=$(awk "BEGIN {printf \"%.1f\", $START_TIME/60}")
    END_TIME=$(awk "BEGIN {print ($START_TIME + $SEGMENT_DURATION)}")
    END_MIN=$(awk "BEGIN {printf \"%.1f\", $END_TIME/60}")

    # Output filename
    OUTPUT_FILE="$OUTPUT_DIR/${FILENAME}_part$(printf "%02d" $((i + 1))).$OUTPUT_FORMAT"

    echo -e "${BLUE}Creating segment $((i + 1))/$SEGMENT_COUNT${NC}"
    echo -e "  Range: ${START_MIN}min - ${END_MIN}min"
    echo -e "  Output: $(basename "$OUTPUT_FILE")"

    # Run ffmpeg
    ffmpeg -i "$INPUT_FILE" \
        -ss "$START_TIME" \
        -t "$SEGMENT_DURATION" \
        -c:a libmp3lame \
        -q:a 2 \
        "$OUTPUT_FILE" \
        -y \
        -loglevel error

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}  ✓ Created successfully${NC}"
    else
        echo -e "${RED}  ✗ Failed to create segment${NC}"
        exit 1
    fi
    echo ""
done

echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}Splitting complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}Created $SEGMENT_COUNT segments in: $OUTPUT_DIR${NC}"
echo ""
echo -e "${BLUE}Segments created:${NC}"
ls -lh "$OUTPUT_DIR/${FILENAME}_part"*".$OUTPUT_FORMAT" | awk '{print "  " $9 " (" $5 ")"}'
echo ""
echo -e "${YELLOW}Note: Adjacent segments have $OVERLAP seconds overlap for transcription continuity${NC}"
