from datetime import datetime, timezone
from supabase_utils import supabase


def delete_expired_files(bucket="encrypted-files"):
    try:
        now = datetime.now(timezone.utc).isoformat()

        response = (
            supabase
            .table("file_metadata")
            .select("*")
            .lte("expiry_time", now)
            .execute()
        )

        expired = response.data or []

        for row in expired:
            try:
                filename = row.get("filename")

                # Delete from storage
                if filename:
                    supabase.storage.from_(bucket).remove([filename])

                # Delete metadata
                supabase.table("file_metadata") \
                    .delete() \
                    .eq("id", row["id"]) \
                    .execute()

            except Exception:
                # Continue even if one file fails
                pass

    except Exception:
        # Prevent entire app crash
        pass