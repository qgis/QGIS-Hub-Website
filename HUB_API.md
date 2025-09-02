# QGIS Resources Hub API Documentation


The `urlpatterns` list routes URLs to views. For more information please see:
[https://docs.djangoproject.com/en/3.2/topics/http/urls/](https://docs.djangoproject.com/en/3.2/topics/http/urls/)

## Authentication

To perform create, update, or delete operations, you must use token-based authentication.

> **NOTE**: You don't need a Token to perform GET request.

**How to obtain an API token:**
1. Log in to the QGIS Hub Website using your credentials.
2. Navigate to **API > Tokens** in the main menu.
3. Click **Generate New Token**.
4. Copy your token immediately, as it will only be displayed once.

Include your token in the `Authorization` header of your API requests:
```
Authorization: Bearer <your_token>
```

## Endpoints

The base URL for the QGIS Hub API is https://hub.qgis.org/api/v1/resources/.

### Available resource types (resource_type)
- `geopackage`
- `3dmodel`
- `style`
- `layerdefinition`
- `model`
- `map`
- `processingscript`
- `screenshot`

### List Resources
- **URL:** `/resources/`
- **Method:** `GET`
- **View:** `ResourceAPIList.as_view()`
- **Name:** `resource-list`
- **Description:** Retrieves a list of all resources.
- **Examples:** 
    - `https://hub.qgis.org/api/v1/resources/`: returns a collection of resources without any filters applied.
    - `https://hub.qgis.org/api/v1/resources/?resource_type=geopackage`: filters the results to only show resources of the type "geopackage".

### Download Resource
- **URL:** `/resource/<uuid:uuid>/`
- **Method:** `GET`
- **View:** `ResourceAPIDownload.as_view()`
- **Name:** `resource-download`
- **Description:** Downloads a specific resource identified by UUID.

### Create Resource
- **URL:** `/resource/create`
- **Method:** `POST`
- **View:** `ResourceCreateView.as_view()`
- **Name:** `resource-create`
- **Description:** Creates a new resource.
- **Request example with cURL:**
    ```sh
    curl --location 'http://localhost:62202/api/v1/resource/create' \
    --header 'Authorization: Bearer <my_token>' \
    --form 'file=@"path/to/the/file.zip"' \
    --form 'thumbnail_full=@"path/to/the/thumbnail.png"' \
    --form 'name="My model"' \
    --form 'description="Little description"' \
    --form 'tags="notag"' \
    --form 'resource_type="model"'
    ```

### Resource Detail
- **URL:** `/resource/<str:resource_type>/<uuid:uuid>/`
- **Methods:** `GET`, `PUT`, `DELETE`
- **View:** `ResourceDetailView.as_view()`
- **Name:** `resource-detail`
- **Description:** Handles the detailed display, update, and deletion of a specific resource based on its type and UUID.
- **Example:**
    To access the details of a resource with type 'style' and UUID '123e4567-e89b-12d3-a456-426614174000':
    ```sh
    GET /resource/style/123e4567-e89b-12d3-a456-426614174000/
    ```
- **Permissions:** Ensure that the user has the necessary permissions (staff or creator) to view, update, or delete the resource details.

## Contributors API

The contributors stats API is included to the Hub for now because it's a small app and this one already includes the necessary dependencies. Also, it will save us from creating a separated server. However, it's recommended to separate it if the contributors APP grows.

The base URL for the QGIS Hub API is https://hub.qgis.org/api/v1/contributors/.

### Commit counts
- **URL:** `<BASE_URL>/<REPO-NAME>/commit-counts`
- **Method:** `GET`
- **View:** `CommitCountList.as_view()`
- **Name:** `commit-counts`
- **Description:** Retrieves the commit counts for all authors.
- **Examples:** 
    - `https://hub.qgis.org/api/v1/contributors/QGIS-Website/commit-counts/`

### Commit counts by author
- **URL:** `<BASE_URL>/<REPO-NAME>/commit-counts/<Author Name>`
- **Method:** `GET`
- **View:** `CommitCountByAuthor.as_view()`
- **Name:** `commit-count-by-author`
- **Description:** Retrieves the commit counts for a specific author. The author name might have changed over the time (set by `git config user.name`) so it's possible to map a comma-separated list of author names to get all counts from the same contributor.
- **Examples:** 
    - `https://hub.qgis.org/api/v1/contributors/QGIS-Website/commit-counts/Xpirix,Lova`
