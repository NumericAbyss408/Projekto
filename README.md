# Zan-Projekto
###### (play on the word "zonpakuto")

tl,dr: localized project folder system. folders on your machine are projects, which can be tagged for tag-search, hold subprojects and store tasks.

## Now for the long of it
Zan-Projekto (or just Projekto) is a system wherein a selected directory holds "projekts": folders on your machine with a `_projesh.dtl` file holding information about said projekt.
When a super folder is selected, a `tagfile.kto` file is created. it is a plaintext JSON structured file that holds all the tags that exist in your project space.
within that same superfolder, live "Projekts". projekts are valid if they hold a non-empty `_projesh.dtl` (which is *also* a plaintext JSON-structured file) composed of name, description, list of tag keys and list of tasks.

The system allows you to create and open projekts, create and assign tags to projekts and write tasks to projekts. it also doubles as a mini search engine, allowing you to search for projekts by both name and additive tag search. 
search is scoped: when a projekt is viewed in the application, the scope shifts such that search looks for descendants of that particular projekt.
search is recursive - all projekts and subprojekts of the formers are returned by search.

# Rationale behind the project
It exists as a means to increase productivity without the drawbacks that come with requiring a network to operate or managing the folder structure such that projects related by type stayed together. especially for creatives or hobbyists in multiple disciplines like image/video editing, 3d asset creation, developers and the like. The goals were to:
- simplify making/finding local projects, so as to more quickly get into the creative swing
- allow folders of different structures to coexist within one ecosystem.

# Future Plans:
- Expand from Windows into Linux and macOS operating systems
- Tweak Theming so as to improve light mode UX
- Add various confirmation popups
