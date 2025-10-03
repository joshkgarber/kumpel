while [[ "$SURE" != "n" && "$SURE" != "y" ]]; do
	read -r -p "Did you change the DB path in db.py to a test db? [y/N] " SURE
    if [[ "$SURE" == "" ]]; then
        SURE="n"
    fi
done

if [ "$SURE" == "n" ]; then
        echo "Cancelled."
        exit 0
fi

python3 -m unittest discover -s .

echo "Remember to change the DB path in db.py back to story.sqlite."
