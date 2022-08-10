import psycopg2

from fastapi import FastAPI


app = FastAPI()
conn = psycopg2.connect(dbname="db", user="postgres")


@app.get("/map")
def get_data(bbox: str):
    if bbox is None:
        return "Bbox is required"
    bbox = bbox.split(",")
    if len(bbox) != 4:
        return "{Bad bbox length}"

    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            json_build_object(
                'type',
                'FeatureCollection',
                'features',
                json_agg(
                    ST_AsGeoJSON(t.*):: json
                )
            )
        FROM
            (
                SELECT
                    wkb_geometry,
                    'yes' as building
                FROM
                    ms_buildings
                WHERE
                    wkb_geometry && ST_SetSRID(
                        ST_MakeBox2D(
                            ST_Point(%s, %s),
                            ST_Point(%s, %s)
                        ),
                        3857
                    )
            ) AS t
        """,
        (bbox),
    )

    return cursor.fetchall()
