# Google Photos Part 1 — Play Store Evidence Case Selection Audit

This document provides a case-by-case audit log of all 190 defensible retrieval evidence records selected in Phase 3B from `raw_reviews_dataset.json` and `evidence_dataset.json`.

---

## Complete Case Audit Table (190 Cases)

| # | External ID | ⭐ | Type | Failure Mode | Clue Type | Stage | Pristine? | Raw Review Excerpt |
| :- | :--- | :-: | :--- | :--- | :--- | :--- | :-: | :--- |
| 1 | `bbdfc7a1-63cb-4553...` | 1★ | `FAILURE` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `HISTORICAL_PRISTINE` | ✅ YES | AI search is slower, less accurate, and more presumptuous than the version we ha... |
| 2 | `62db9478-859f-4268...` | 1★ | `FAILURE` | `INCOMPLETE_RESULTS` | `ALBUM_CONTAINER` | `STAGE_1_LEXICAL` | — | I've been thinking about writing a review since the change in the way I can edit... |
| 3 | `9915bc29-b7bd-424c...` | 1★ | `FAILURE` | `PERSON_NOT_RECOGNIZED` | `ALBUM_CONTAINER` | `STAGE_1_LEXICAL` | — | i really don't like this app. i don't like the 'moments' it randomly creates tha... |
| 4 | `ee2f50f5-fc3a-4f39...` | 1★ | `FAILURE` | `INCOMPLETE_RESULTS` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | It won't let me merge peoples labels or import my photos from Google drive. So a... |
| 5 | `f4cd708a-8395-46ac...` | 1★ | `FAILURE` | `MANUAL_SCROLLING_REQUIRED` | `TEMPORAL_DATE` | `STAGE_2_SEMANTIC_EXPANSION` | — | I hate the latest update. please change it back. it takes so long to edit someth... |
| 6 | `d6276e7a-5d2b-4533...` | 1★ | `NEUTRAL` | `CANNOT_FIND_PHOTO` | `NATURAL_LANGUAGE_DESCRIPTION` | `HISTORICAL_PRISTINE` | ✅ YES | Photos used to be the perfect photos app. it had the best search funding of any ... |
| 7 | `897711fc-0fb7-457a...` | 1★ | `FAILURE` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | Every update the app gets worse and worse. The options less and less. And AI slo... |
| 8 | `d4b8dd23-bb7f-491f...` | 1★ | `FAILURE` | `MANUAL_SCROLLING_REQUIRED` | `ALBUM_CONTAINER` | `STAGE_2_SEMANTIC_EXPANSION` | — | This app DOES NOT duplicate photos, so if you plan on keeping your photos in the... |
| 9 | `180baa76-e72d-41c1...` | 1★ | `FAILURE` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | I am paying for Google photo storage for 3TB.... yet there is no customer suppor... |
| 10 | `24478ad8-ae32-4f50...` | 1★ | `FAILURE` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_1_LEXICAL` | — | Photos is forcing AI generated "creations" that use your photos. If you want to ... |
| 11 | `5392a1d0-afec-4227...` | 1★ | `FAILURE` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | I'm a long time, heavy user of Google Photos & an Alphabet stockholder. Until ye... |
| 12 | `fe4934a1-2aba-4ab4...` | 1★ | `FAILURE` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | First of all, when people write a review, they are looking for a solution, not f... |
| 13 | `46ca1057-94f2-4ede...` | 1★ | `FAILURE` | `WRONG_PERSON` | `PERSON_FACE` | `HISTORICAL_PRISTINE` | ✅ YES | The face tagging feature is poor and it's had the same issues for years. Unable ... |
| 14 | `2865fbd1-e82d-4490...` | 1★ | `FAILURE` | `CANNOT_FIND_PHOTO` | `TEMPORAL_DATE` | `HISTORICAL_PRISTINE` | ✅ YES | Search doesn't work like it used to, so it kind of makes this app worthless to m... |
| 15 | `3c905b64-706d-4481...` | 1★ | `FAILURE` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | Something annoying happened in the recent version! I usually edit pictures and s... |
| 16 | `fc669de5-7c8c-4bd8...` | 1★ | `FAILURE` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `HISTORICAL_PRISTINE` | ✅ YES | One of the main things I really like about this app and use it for is face group... |
| 17 | `17ff7e6d-5871-4b4a...` | 1★ | `FAILURE` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_2_SEMANTIC_EXPANSION` | — | edit: I fixed the problem, used an apk to download version 7.90! the last update... |
| 18 | `9c70c590-a15f-4cff...` | 1★ | `FAILURE` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | Unable to separate folders and the continued invasion of privacy. I have a few f... |
| 19 | `1e928442-696c-4c02...` | 1★ | `FAILURE` | `CANNOT_FIND_PHOTO` | `SEARCH_KEYWORD` | `STAGE_2_SEMANTIC_EXPANSION` | — | MY PHOTOS ARE MISSING!!!! My old photos that were backed up and I could see earl... |
| 20 | `0a4c0ec5-ddea-4a62...` | 1★ | `FAILURE` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `HISTORICAL_PRISTINE` | ✅ YES | After a certain amount of time, the app stops labeling photos of a certain perso... |
| 21 | `b0b41afd-959c-4ce5...` | 1★ | `FAILURE` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_2_SEMANTIC_EXPANSION` | — | See all the reasons above and below my review. Pictures are hidden in folders an... |
| 22 | `e01d05dc-be47-4429...` | 1★ | `FAILURE` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | You can no longer search your photos without turning on Backup. Time for a new A... |
| 23 | `c8aabd3e-2292-47b5...` | 1★ | `FAILURE` | `MANUAL_SCROLLING_REQUIRED` | `SEARCH_KEYWORD` | `STAGE_1_LEXICAL` | — | This app is frustrating. Navigating videos is really difficult. It jumps while m... |
| 24 | `1f68ab12-a59a-4dc6...` | 1★ | `FAILURE` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_1_LEXICAL` | — | They removed the ability to see photo information. it used to be if you clicked ... |
| 25 | `6cf35a27-cd8e-4f3b...` | 1★ | `FAILURE` | `INCOMPLETE_RESULTS` | `ALBUM_CONTAINER` | `STAGE_2_SEMANTIC_EXPANSION` | — | Hate it. I cant stand how it automatically stores my photos in Numerous differen... |
| 26 | `56b98d58-f989-4991...` | 1★ | `FAILURE` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | Hate the update, no longer able to search without using Gemini, which I also hat... |
| 27 | `c3d63140-a872-4b55...` | 1★ | `FAILURE` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | Locked Folder is missing from my Google Photos app. I checked Collections, but t... |
| 28 | `9c5b323d-c364-4ee6...` | 1★ | `FAILURE` | `INCOMPLETE_RESULTS` | `SEARCH_KEYWORD` | `STAGE_2_SEMANTIC_EXPANSION` | — | Completely messed up the search function. It used to be really simple to search,... |
| 29 | `31ab9f12-ffb4-4711...` | 1★ | `FAILURE` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | Search used to be effortless, but the latest updates ruined it. It can't locate ... |
| 30 | `5aba443b-ae59-44e2...` | 1★ | `FAILURE` | `INCOMPLETE_RESULTS` | `OCR_DOCUMENT_TEXT` | `STAGE_1_LEXICAL` | — | there is so many features which annoy me yet i cant turn them off. auto album is... |
| 31 | `f38f4a2f-7eb0-453b...` | 2★ | `FAILURE` | `PERSON_NOT_RECOGNIZED` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_1_LEXICAL` | — | Their is a lot to like about the photo app. the editing tools are great and very... |
| 32 | `586c10e9-9c09-4447...` | 2★ | `FAILURE` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_2_SEMANTIC_EXPANSION` | — | Used to be a good, March update ruined it. Moved all the editing options. onto d... |
| 33 | `dc40fa6f-05fe-43fa...` | 2★ | `FAILURE` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_1_LEXICAL` | — | This app is practically unusable anymore. The search engine doesn't ever freakin... |
| 34 | `e48f580e-9687-4819...` | 2★ | `FAILURE` | `INCOMPLETE_RESULTS` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | Service has steadily declined for years now. Lots of features just completely do... |
| 35 | `fb853800-f7d4-4c6c...` | 2★ | `FAILURE` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_1_LEXICAL` | — | this app used to be perfect, but the quality has gone downhill. the new ai searc... |
| 36 | `bd1afa26-2281-4093...` | 2★ | `FAILURE` | `IRRELEVANT_RESULTS` | `NATURAL_LANGUAGE_DESCRIPTION` | `HISTORICAL_PRISTINE` | ✅ YES | Loved Google Photos. Always demonstrating to people how easy it was to find a ph... |
| 37 | `60cc6956-735e-4794...` | 2★ | `FAILURE` | `WRONG_PERSON` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | It was great but in collections it only sometimes let's me merge faces with coll... |
| 38 | `544c13cb-c662-4b03...` | 2★ | `FAILURE` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | Poor usability. Can't select a bunch of photos to move them to an album AND arch... |
| 39 | `2d623efd-0948-4012...` | 2★ | `FAILURE` | `CANNOT_FIND_PHOTO` | `TEMPORAL_DATE` | `HISTORICAL_PRISTINE` | ✅ YES | Within the past couple weeks, I'm unable to use search - all searches return no ... |
| 40 | `b9ab5ac3-1cab-497b...` | 2★ | `FAILURE` | `CANNOT_FIND_PHOTO` | `SEARCH_KEYWORD` | `STAGE_1_LEXICAL` | — | I went into the app looking for something to send my sister only to discover tha... |
| 41 | `302cc840-fa8c-4a24...` | 2★ | `FAILURE` | `REQUIRES_EXACT_DATE` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_2_SEMANTIC_EXPANSION` | — | The latest version of the app doesn't seem to order pictures chronologically by ... |
| 42 | `be430887-186c-448a...` | 2★ | `FAILURE` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | Not intuitive for digital art, which most of my pictures are. The Memories and F... |
| 43 | `3a3a8915-8a45-4e12...` | 2★ | `FAILURE` | `WRONG_PERSON` | `PERSON_FACE` | `STAGE_2_SEMANTIC_EXPANSION` | — | Even with the latest updates, it would not let you edit or add location to the b... |
| 44 | `1ea9af4d-293c-4c0f...` | 2★ | `FAILURE` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_2_SEMANTIC_EXPANSION` | — | I used to love Google photos but now thinking of moving to iOS thanks to the lat... |
| 45 | `5588dac1-6b61-46ea...` | 2★ | `FAILURE` | `INCOMPLETE_RESULTS` | `ALBUM_CONTAINER` | `STAGE_2_SEMANTIC_EXPANSION` | — | This app continues to get enshitified. In 2026 I thought I could send an album t... |
| 46 | `6ae082ad-60ec-472d...` | 2★ | `FAILURE` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | The latest forced update has totally ruined the interface and usability. I pay f... |
| 47 | `e5ea2c92-3df6-4b8e...` | 2★ | `FAILURE` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_2_SEMANTIC_EXPANSION` | — | Incredibly tedious, barely fit for purpose, frustratingly slow. • Often takes 30... |
| 48 | `b472a0e9-a4d8-4d08...` | 2★ | `FAILURE` | `REQUIRES_EXACT_DATE` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_2_SEMANTIC_EXPANSION` | — | Horrible layout now with odd photos extra large. I want them all thumbnail size.... |
| 49 | `08146e97-2c71-4eb5...` | 2★ | `FAILURE` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_2_SEMANTIC_EXPANSION` | — | Where are my missing album pictures that I uploaded from my Galaxy phone !Still ... |
| 50 | `4fceb7fc-7f57-4831...` | 2★ | `FAILURE` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_1_LEXICAL` | — | I don't like how the app constantly rearrange photos, making them very difficult... |
| 51 | `069518e9-1250-41a0...` | 2★ | `FAILURE` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `HISTORICAL_PRISTINE` | ✅ YES | Ongoing issue for some time now. It fails to recognise pets in a lot of photos. ... |
| 52 | `3ed3260f-c301-4e52...` | 2★ | `FAILURE` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_2_SEMANTIC_EXPANSION` | — | I'm not too excited about how it groups my pictures together. Then, I have a vid... |
| 53 | `7f6fcc90-54db-4eef...` | 2★ | `FAILURE` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | Lowering my rating until my issue is fixed. Cannot create new faces or add photo... |
| 54 | `4c948ab7-3878-480e...` | 2★ | `FAILURE` | `CONTEXT_NOT_UNDERSTOOD` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | Specifically purchased the type of phone I have for this photos app. For years I... |
| 55 | `f58f0d55-7b9c-426c...` | 2★ | `NEUTRAL` | `MANUAL_SCROLLING_REQUIRED` | `TEMPORAL_DATE` | `HISTORICAL_PRISTINE` | ✅ YES | organization difficulty. it's great having folders but I wish they'd disappear f... |
| 56 | `07b94035-bbb6-411a...` | 2★ | `FAILURE` | `INCOMPLETE_RESULTS` | `OCR_DOCUMENT_TEXT` | `STAGE_1_LEXICAL` | — | "Google Photos needs to add a proper selective backup feature. Currently, it bac... |
| 57 | `b4ad14c0-e53a-4072...` | 2★ | `FAILURE` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_2_SEMANTIC_EXPANSION` | — | Recent updates have introduced a bunch of bugs that make it really inconvenient ... |
| 58 | `7ff95532-c66a-4b03...` | 2★ | `FAILURE` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | still a horror show of usability for editing (no I'm not going to use Gemini to ... |
| 59 | `23395dc1-410a-4f67...` | 2★ | `FAILURE` | `WRONG_PERSON` | `PERSON_FACE` | `STAGE_2_SEMANTIC_EXPANSION` | — | frustrated by the app changing the layout. I like the app to open on the camera ... |
| 60 | `0f8b93e7-c35f-4fd1...` | 2★ | `FAILURE` | `IRRELEVANT_RESULTS` | `OCR_DOCUMENT_TEXT` | `STAGE_1_LEXICAL` | — | automatic backup is nice, although it is very annoying that there is no easy way... |
| 61 | `23dacf60-656a-44e6...` | 2★ | `FAILURE` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | very bad navigation. whenever I have to send or share a photo I never find it in... |
| 62 | `3453c13d-fa12-4c32...` | 2★ | `FAILURE` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_1_LEXICAL` | — | Far too many changes behind the scenes. A while back my pictures were backed up ... |
| 63 | `65d73c75-b625-4cfd...` | 2★ | `FAILURE` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_1_LEXICAL` | — | PLEASE FIX ASAP! WHERE DO THE EDITED PHOTOS GO? As soon as you finish editing an... |
| 64 | `4dbb0510-81f3-4f9d...` | 2★ | `FAILURE` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | This latest update to remove the months is awful. I can't find the pictures I wa... |
| 65 | `b3550015-a619-4093...` | 2★ | `FAILURE` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_2_SEMANTIC_EXPANSION` | — | latest update not good. ui was fine before now just looks like the iOS photos ap... |
| 66 | `72d1ac92-33ca-4bb6...` | 2★ | `FAILURE` | `CONTEXT_NOT_UNDERSTOOD` | `OCR_DOCUMENT_TEXT` | `STAGE_1_LEXICAL` | — | It's rubbish that when you've opted to backup WhatsApp photos automatically, Goo... |
| 67 | `163d2039-63f6-4cc1...` | 2★ | `FAILURE` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | The app layout used to be so good...but now all the photos appear together... wi... |
| 68 | `e6125bed-6834-4e18...` | 2★ | `FAILURE` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_2_SEMANTIC_EXPANSION` | — | I do not like this update. The lack of separation from date to date makes it dif... |
| 69 | `36ca6fef-c61c-4f7f...` | 2★ | `FAILURE` | `MANUAL_SCROLLING_REQUIRED` | `SEARCH_KEYWORD` | `STAGE_1_LEXICAL` | — | The latest change to land makes it look like a wannabe for the iPhone. Suddenly ... |
| 70 | `1224b82e-1b51-4a55...` | 2★ | `FAILURE` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | Google is well on the way to destroying what used to be very good app with their... |
| 71 | `e11c28e9-173b-42b8...` | 2★ | `FAILURE` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_2_SEMANTIC_EXPANSION` | — | Over time, the app has steadily gotten worse. Consistently, features have been r... |
| 72 | `7ef6f461-8e72-480f...` | 2★ | `FAILURE` | `MANUAL_SCROLLING_REQUIRED` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | app is good, perfect to keep a hold of pictures but the new update of the galler... |
| 73 | `8321a8e6-27b3-45d4...` | 2★ | `FAILURE` | `INCOMPLETE_RESULTS` | `OCR_DOCUMENT_TEXT` | `STAGE_1_LEXICAL` | — | Google Photos SEEMED to have improved but took a downward turn when, in back-up,... |
| 74 | `4c3065ba-7660-4a99...` | 2★ | `FAILURE` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | I used to really like this app but things have gotten so confusing that it's nea... |
| 75 | `0b28df7f-204b-4744...` | 2★ | `FAILURE` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | The people & pet grouping and then auto-updating albums are fantastic features, ... |
| 76 | `9957c225-6b93-4205...` | 2★ | `FAILURE` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | I don't like the new update at all. why are some pictures bigger than others? it... |
| 77 | `f141d621-96df-4ad1...` | 2★ | `FAILURE` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | I deleted a bunch of my photos and the photos icon on the screen of my phone dis... |
| 78 | `fcd33f0b-d743-46de...` | 2★ | `FAILURE` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | I was expecting photos will get added automatically in People and Pet Section bu... |
| 79 | `40ee811f-5fcd-4d40...` | 2★ | `FAILURE` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | Every other day this app sends me a notification like "Say hello to this familia... |
| 80 | `d926fd85-3427-4c3b...` | 2★ | `NEUTRAL` | `MANUAL_SCROLLING_REQUIRED` | `TEMPORAL_DATE` | `HISTORICAL_PRISTINE` | ✅ YES | Would be great to be able to have the search feature in locked folder. Ridiculou... |
| 81 | `a2bee9ea-3dfd-431d...` | 2★ | `NEUTRAL` | `CANNOT_FIND_PHOTO` | `TEMPORAL_DATE` | `HISTORICAL_PRISTINE` | ✅ YES | the latest update is garbage. the search function is useless. I search up human,... |
| 82 | `166741f3-b0d7-40b5...` | 3★ | `NEUTRAL` | `INCOMPLETE_RESULTS` | `ALBUM_CONTAINER` | `STAGE_2_SEMANTIC_EXPANSION` | — | Motorola user here 👋🏻! Us people don't have a built-in photo gallery, and Google... |
| 83 | `fac36b13-cb88-4c52...` | 3★ | `NEUTRAL` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_1_LEXICAL` | — | Good for photo storage and searching, but it sends too many memories/themed noti... |
| 84 | `3ae7ed7f-72b4-4872...` | 3★ | `NEUTRAL` | `MANUAL_SCROLLING_REQUIRED` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_1_LEXICAL` | — | Few feedback . If I search for an album, currently only those uploaded by me are... |
| 85 | `53ce2f32-49ee-4f6a...` | 3★ | `NEUTRAL` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_1_LEXICAL` | — | The apps good and everything.. but it doesn't retain the photos in the original ... |
| 86 | `e5c9be75-7682-47dc...` | 3★ | `FAILURE` | `OTHER` | `ALBUM_CONTAINER` | `HISTORICAL_PRISTINE` | ✅ YES | Change is sometimes difficult. Finding specific photos varies between easy and c... |
| 87 | `2620e449-2b67-446b...` | 3★ | `NEUTRAL` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_2_SEMANTIC_EXPANSION` | — | I would give this 5 stars for being easy to use and easy to find my pictures, bu... |
| 88 | `9bf5689f-66c3-4ea9...` | 3★ | `NEUTRAL` | `INCOMPLETE_RESULTS` | `OCR_DOCUMENT_TEXT` | `STAGE_1_LEXICAL` | — | My favorites on my Motorola keep getting removed from that folder for no reason!... |
| 89 | `475a0a0f-bcd5-47f8...` | 3★ | `NEUTRAL` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `HISTORICAL_PRISTINE` | ✅ YES | With the last update or couple, the facial recognition got SO bad. It used to be... |
| 90 | `62d3d528-6a96-457b...` | 3★ | `NEUTRAL` | `MANUAL_SCROLLING_REQUIRED` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_2_SEMANTIC_EXPANSION` | — | Please put the monthly view back to small thumbnails only. The random large phot... |
| 91 | `a063c498-e373-40ef...` | 3★ | `NEUTRAL` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_1_LEXICAL` | — | Another Google app that's becoming more and more infuriatingly unusable by the d... |
| 92 | `9f712c43-3f31-42fd...` | 3★ | `NEUTRAL` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | It's mostly good but some photos don't have my face highlighted or those of othe... |
| 93 | `0f519c2f-e4a5-4b13...` | 3★ | `NEUTRAL` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_2_SEMANTIC_EXPANSION` | — | I like the whole timeline idea and a few of the other features. I would really l... |
| 94 | `7943b1f8-2a4e-4a2a...` | 3★ | `NEUTRAL` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_2_SEMANTIC_EXPANSION` | — | would give it a 5 but I can't add photos to the faces folders. There are issues ... |
| 95 | `bd953071-c12e-49d1...` | 3★ | `NEUTRAL` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | Great editing features. It would be improved hugely if the facial organisation a... |
| 96 | `b7217d13-fac5-42ab...` | 3★ | `NEUTRAL` | `MANUAL_SCROLLING_REQUIRED` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | Miss the old separation of photos by dates that left a break. This new continuou... |
| 97 | `d9a256f3-fb6e-42af...` | 3★ | `NEUTRAL` | `INCOMPLETE_RESULTS` | `OCR_DOCUMENT_TEXT` | `STAGE_1_LEXICAL` | — | app is not bad, i use lot's of great features, but i can't see all the images - ... |
| 98 | `15bb71f4-75a3-4829...` | 3★ | `NEUTRAL` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_2_SEMANTIC_EXPANSION` | — | Very useful feature "Conversation" is hidden God knows where... UI became extrem... |
| 99 | `2ffe8362-763b-4ec8...` | 3★ | `NEUTRAL` | `PERSON_NOT_RECOGNIZED` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_1_LEXICAL` | — | Facial recognition works great. Searching for objects or places also works well.... |
| 100 | `c9e7d180-0f7f-48b1...` | 3★ | `NEUTRAL` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | every time this updates it gets more difficult to find photos. Response isn't he... |
| 101 | `27f71481-d858-4e26...` | 3★ | `NEUTRAL` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | update after Dev response: it's not working guys. there is a bug and I can prove... |
| 102 | `b54b49c3-d528-44fb...` | 3★ | `FAILURE` | `CANNOT_FIND_PHOTO` | `NATURAL_LANGUAGE_DESCRIPTION` | `HISTORICAL_PRISTINE` | ✅ YES | I can no longer search my photos for people, colors, objects or words (etc). try... |
| 103 | `582d4584-bcb2-42be...` | 3★ | `NEUTRAL` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | this app is so frustrating, and I always struggle to find the feature I want. to... |
| 104 | `a682d12c-0d6a-469f...` | 3★ | `NEUTRAL` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | Its Greate for Personnel use but its Not Good for Business Media content organis... |
| 105 | `da80cc2c-2fba-46b4...` | 3★ | `NEUTRAL` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | It's missing something! I want to move my pictures to an album and those photos ... |
| 106 | `d2b35a60-2fa9-4a14...` | 3★ | `NEUTRAL` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | some time ago face detection became really horrid - from a great and useful feat... |
| 107 | `2cadc2d5-808b-4f2d...` | 3★ | `NEUTRAL` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_1_LEXICAL` | — | I appreciate the restoration of perspective, but it has not been restored in Vid... |
| 108 | `bfb0d9d2-17f9-416a...` | 3★ | `NEUTRAL` | `MANUAL_SCROLLING_REQUIRED` | `SEARCH_KEYWORD` | `STAGE_1_LEXICAL` | — | PLEASE add the option to size all previews in the grid-based gallery view the sa... |
| 109 | `d18eacb5-54d4-4986...` | 3★ | `NEUTRAL` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | for some reason, my backed up photos are not recognised and categorised by face.... |
| 110 | `9bae19b0-2f3a-41a7...` | 3★ | `FAILURE` | `OTHER` | `SEARCH_KEYWORD` | `HISTORICAL_PRISTINE` | ✅ YES | the app has been so poor recently with the search keywords. even when your photo... |
| 111 | `a24bf0d7-b924-41fb...` | 3★ | `NEUTRAL` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | The crop tool glitches if you use the auto crop and then try to adjust it. You c... |
| 112 | `11611d40-f237-4d95...` | 3★ | `NEUTRAL` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_1_LEXICAL` | — | where did the search feature go? I have to "ask" now? Will you stop trying to "i... |
| 113 | `aa7ec930-3d67-496c...` | 3★ | `NEUTRAL` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | All are Perfect but, once i open photos app, it's showing main menu and select a... |
| 114 | `bf91ca2f-fe93-40c2...` | 3★ | `NEUTRAL` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_2_SEMANTIC_EXPANSION` | — | Great app and way to keep the phone tidy, however, there should be a way to disa... |
| 115 | `422f2a98-0ddf-4525...` | 3★ | `NEUTRAL` | `INCOMPLETE_RESULTS` | `ALBUM_CONTAINER` | `STAGE_2_SEMANTIC_EXPANSION` | — | Annoying Bug. Starting from about July 2026, if you edit a photo (even just rota... |
| 116 | `ae175797-6b16-4e8b...` | 3★ | `NEUTRAL` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | I am facing an issue with my Google Photos app and would appreciate your help in... |
| 117 | `d3a76c5e-91de-46f0...` | 3★ | `NEUTRAL` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_2_SEMANTIC_EXPANSION` | — | Best app ever🤩🤩, been using it for 3 years now but honestly I'm not really a fan... |
| 118 | `31175e77-203d-40ab...` | 4★ | `SUCCESS` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_2_SEMANTIC_EXPANSION` | — | The app is so nice as far..I even purchased storage..but it would be nice if we ... |
| 119 | `2e38a63c-962a-4b57...` | 4★ | `SUCCESS` | `MANUAL_SCROLLING_REQUIRED` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | A true gallery! Much more than just a place dumped with all your photos. Few Imp... |
| 120 | `645778f9-8df3-4592...` | 4★ | `SUCCESS` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_1_LEXICAL` | — | Comparing to Flickr the upload and organization feature is better. Loved the min... |
| 121 | `90ad0544-cb78-439e...` | 4★ | `SUCCESS` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_1_LEXICAL` | — | It's terrible, it backs the pics up before I get a chance to edit them, then I c... |
| 122 | `e3bc1db6-4d55-4bf6...` | 4★ | `SUCCESS` | `NONE` | `SEARCH_KEYWORD` | `STAGE_1_LEXICAL` | — | the app is actually good. you can do a lot of things to edit photos or videos, t... |
| 123 | `d874566f-b1d1-4ea6...` | 4★ | `NEUTRAL` | `OTHER` | `PERSON_FACE` | `HISTORICAL_PRISTINE` | ✅ YES | How did I just discover Google Photos now 🙃 but I do have some complaints 1: alo... |
| 124 | `2c69117c-ccdc-4ca1...` | 4★ | `SUCCESS` | `CANNOT_FIND_PHOTO` | `OCR_DOCUMENT_TEXT` | `STAGE_1_LEXICAL` | — | When the Screenshots folder is opened it displays ‘photos missing from search Tu... |
| 125 | `cbb835d0-f0c6-4771...` | 4★ | `SUCCESS` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | photos is great, but the new update they put in for music playing over the "memo... |
| 126 | `b6113344-54ee-4c99...` | 4★ | `SUCCESS` | `NONE` | `SEARCH_KEYWORD` | `STAGE_1_LEXICAL` | — | Since my last review the app has improved dramatically. However, there is still ... |
| 127 | `1d0cc16e-b136-4439...` | 4★ | `SUCCESS` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | App is great. Lots of things are better then before and the team have listened t... |
| 128 | `0ccde87d-b1e7-4e56...` | 4★ | `SUCCESS` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | I've been using this app for many years now!! and I'm disappointed to say that t... |
| 129 | `b573ae36-9ac1-4e46...` | 4★ | `SUCCESS` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | Looks like you've finally fixed the screenshot folder access. Recent updates wer... |
| 130 | `16ea6024-014c-497b...` | 4★ | `SUCCESS` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | Lacks editing options. Hope you could add more such as adding resizable shapes (... |
| 131 | `e76d70f5-5a9a-48c7...` | 4★ | `SUCCESS` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_2_SEMANTIC_EXPANSION` | — | I select photos from my gallery and back them up to Google Photos. They appear i... |
| 132 | `7ec8ffcc-0b1c-4be1...` | 4★ | `SUCCESS` | `IRRELEVANT_RESULTS` | `OCR_DOCUMENT_TEXT` | `STAGE_1_LEXICAL` | — | currently use it to back up my photos. only thing that would make this better wo... |
| 133 | `7e2755dc-591c-40ae...` | 4★ | `SUCCESS` | `NONE` | `OCR_DOCUMENT_TEXT` | `STAGE_1_LEXICAL` | — | it's good but the fact that it doesn't show you everything Immediately makes me ... |
| 134 | `d306f2a8-e48f-461c...` | 4★ | `SUCCESS` | `NONE` | `SEARCH_KEYWORD` | `STAGE_1_LEXICAL` | — | Guys, why don't you provide a direct download feature in the application so that... |
| 135 | `78e37e80-40b7-4e0e...` | 4★ | `SUCCESS` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | Please add subfolders to the Locked Folder in Google Photos. It would make it mu... |
| 136 | `048d059c-a5d9-41b6...` | 4★ | `NEUTRAL` | `NONE` | `PERSON_FACE` | `HISTORICAL_PRISTINE` | ✅ YES | I would really like to be able to label my horse under the people and pets categ... |
| 137 | `c7ead999-1493-4f99...` | 4★ | `SUCCESS` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | It would be a 5 star but, the app's face recognition and matching features, prev... |
| 138 | `466488fc-01ac-4fe0...` | 4★ | `SUCCESS` | `CANNOT_FIND_PHOTO` | `ALBUM_CONTAINER` | `STAGE_1_LEXICAL` | — | ✨ Can't search the album, when I'm in a albums, I want to add some photos from t... |
| 139 | `9c9fc135-f3d2-46b2...` | 4★ | `SUCCESS` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_1_LEXICAL` | — | Good cannot find a magic eraser in the app basic edit like crop and brightness o... |
| 140 | `ffd18ead-34a1-40a8...` | 4★ | `SUCCESS` | `NONE` | `PERSON_FACE` | `HISTORICAL_PRISTINE` | ✅ YES | I love it, but please add a direct button to merge face groups. The AI constantl... |
| 141 | `180005cb-b566-4430...` | 4★ | `FAILURE` | `NONE` | `PERSON_FACE` | `HISTORICAL_PRISTINE` | ✅ YES | I have questions & need some answers !! I've been using this app since 2017. I n... |
| 142 | `fb00ff91-2415-432d...` | 4★ | `SUCCESS` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | not being able to group albums into folders is driving me crazy, especially sinc... |
| 143 | `407fb276-32b4-48f6...` | 5★ | `SUCCESS` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | Excellent Photo Management App! Google Photos is one of the most useful apps for... |
| 144 | `26476128-9573-4e06...` | 5★ | `SUCCESS` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | They added search to the Add To Album popup! Someone *is* reading all those feed... |
| 145 | `24e628d4-e435-4971...` | 5★ | `SUCCESS` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | Google Photos is one of the best apps for storing and organizing photos. It auto... |
| 146 | `9a1e075b-c040-4df6...` | 5★ | `SUCCESS` | `NONE` | `SEARCH_KEYWORD` | `STAGE_1_LEXICAL` | — | Google Photos is an excellent app for storing, organizing, and backing up photos... |
| 147 | `6f455c4a-9f1d-4bbe...` | 5★ | `SUCCESS` | `NONE` | `SEARCH_KEYWORD` | `STAGE_1_LEXICAL` | — | Google Photos is an excellent app for storing, organizing, and managing photos a... |
| 148 | `a34a5808-0ec3-4f88...` | 5★ | `SUCCESS` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_2_SEMANTIC_EXPANSION` | — | Update. I can separate by date again!!! Thank you Google photos!! As of 23Jul202... |
| 149 | `eaedd629-d50b-43d8...` | 5★ | `SUCCESS` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_2_SEMANTIC_EXPANSION` | — | Hate the new update. Grouping the photos by date and being able to select a whol... |
| 150 | `53fd4734-7980-43f1...` | 5★ | `SUCCESS` | `NONE` | `SEARCH_KEYWORD` | `STAGE_1_LEXICAL` | — | Absolutely love Google Photos! The automatic backup gives me peace of mind that ... |
| 151 | `5fb2385c-001d-42ea...` | 5★ | `SUCCESS` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_2_SEMANTIC_EXPANSION` | — | Love it! All my photos in one place and it even has features to organize photos ... |
| 152 | `3166efe3-e029-4db4...` | 5★ | `SUCCESS` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | Google Photos is an excellent app for storing, organizing, and sharing photos an... |
| 153 | `7a0531cb-1278-4c51...` | 5★ | `SUCCESS` | `NONE` | `SEARCH_KEYWORD` | `STAGE_1_LEXICAL` | — | Google Photos is a very useful and easy-to-use app for storing, organizing and v... |
| 154 | `a6381079-a985-4176...` | 5★ | `SUCCESS` | `NONE` | `SEARCH_KEYWORD` | `STAGE_1_LEXICAL` | — | Google Photos is the best app for storing and organizing memories! Automatic bac... |
| 155 | `c97eca3d-d851-483d...` | 5★ | `SUCCESS` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | one of the best photo apps out there, especially around managing the mass amount... |
| 156 | `ada4c676-9822-4a94...` | 5★ | `SUCCESS` | `NONE` | `NATURAL_LANGUAGE_DESCRIPTION` | `HISTORICAL_PRISTINE` | ✅ YES | I love the new Ai additional help in the search bar. However, when I request a s... |
| 157 | `144ec96c-cff8-4927...` | 5★ | `NEUTRAL` | `NONE` | `TEMPORAL_DATE` | `HISTORICAL_PRISTINE` | ✅ YES | The app is good, but I wish the photos in albums could be zoomed out like in the... |
| 158 | `36f90c6a-1d3d-4340...` | 5★ | `SUCCESS` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_2_SEMANTIC_EXPANSION` | — | Great app, awesome! It really helps, now I shared a link, easy to find my other ... |
| 159 | `d06e38be-055d-4051...` | 5★ | `SUCCESS` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | Google Photos is simply the best photo management app I've ever used. The backup... |
| 160 | `7247f045-33e3-4ab2...` | 5★ | `SUCCESS` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | Your precious moments are safe with Google photos, backing up every pic so you c... |
| 161 | `67176cd9-ca57-4671...` | 5★ | `SUCCESS` | `NONE` | `ALBUM_CONTAINER` | `STAGE_1_LEXICAL` | — | Google Photos is the most useful app for storing and organizing photos. The auto... |
| 162 | `17aaa967-60af-4dcc...` | 5★ | `SUCCESS` | `NONE` | `SEARCH_KEYWORD` | `STAGE_2_SEMANTIC_EXPANSION` | — | I am hoping that this App is easy to use and I am able to find my photos and vid... |
| 163 | `0d4f8a16-ebfc-4558...` | 5★ | `SUCCESS` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | Pros: * Photos and videos are backed up securely and automatically. * Smart sear... |
| 164 | `ca63932c-b9ba-45b0...` | 5★ | `SUCCESS` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | easy app to save,organize,navigate, and share photos taken from your camera app,... |
| 165 | `351c3f52-da6d-4deb...` | 5★ | `SUCCESS` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | Solid, with a few rough edges Genuinely one of the best-executed apps on my phon... |
| 166 | `f9aa7659-bba1-4e66...` | 5★ | `SUCCESS` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_1_LEXICAL` | — | Google Photos is an excellent app for backing up and organizing photos and video... |
| 167 | `6e8c1980-8b3a-4a8c...` | 5★ | `SUCCESS` | `NONE` | `SEARCH_KEYWORD` | `STAGE_1_LEXICAL` | — | Google Photos is fantastic for backing up all my pictures automatically. The sea... |
| 168 | `788e1618-71e0-4281...` | 5★ | `SUCCESS` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | Google Photos is an absolute masterpiece. The cloud backup is seamless, and the ... |
| 169 | `2bf42470-548a-493b...` | 5★ | `SUCCESS` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | They added search to the Add To Album popup! Someone *is* reading all those feed... |
| 170 | `60848b00-a833-4697...` | 5★ | `SUCCESS` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_1_LEXICAL` | — | Google Photos is one of the best photo management apps! The backup, search, edit... |
| 171 | `a475d0c4-6b07-4654...` | 5★ | `SUCCESS` | `NONE` | `SEARCH_KEYWORD` | `STAGE_1_LEXICAL` | — | simply superb This app is excellent. It makes it easy to back up my photos and v... |
| 172 | `5b31bb2b-d271-41c0...` | 5★ | `SUCCESS` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_1_LEXICAL` | — | I love the daily memories feature. But, just as all other photos app its difficu... |
| 173 | `9eef7f53-d4fe-46e4...` | 5★ | `SUCCESS` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | The interface is so nice and clean! Old photos are easy to find and the albums a... |
| 174 | `b0b5c01b-0078-4d6b...` | 5★ | `SUCCESS` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_2_SEMANTIC_EXPANSION` | — | Google Photos helps me find my photos of everything I've taken a picture of like... |
| 175 | `74079f57-09fa-4205...` | 5★ | `SUCCESS` | `NONE` | `SEARCH_KEYWORD` | `STAGE_1_LEXICAL` | — | My app is not giving me all of the coupons that I choose. I tried to search for ... |
| 176 | `49b1e413-9cd4-4e58...` | 5★ | `SUCCESS` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | amazing app it's the only photo app I use it does everything u can transfer pics... |
| 177 | `04e7dd7a-7f17-42d7...` | 5★ | `SUCCESS` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_2_SEMANTIC_EXPANSION` | — | I have had Google devices , now I have the Pixel 9 pro, love this app and the Go... |
| 178 | `821b9c14-cf6b-4c54...` | 1★ | `FAILURE` | `CANNOT_FIND_PHOTO` | `SEARCH_KEYWORD` | `STAGE_1_LEXICAL` | — | Can't find my device photos even if I backed everything up. I can't also find it... |
| 179 | `03ba0f04-e8ec-42f6...` | 1★ | `FAILURE` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_1_LEXICAL` | — | I can't find any of my photos that they took off of my gallery. I hate Google ph... |
| 180 | `3faa0e9e-69df-4df8...` | 1★ | `FAILURE` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_2_SEMANTIC_EXPANSION` | — | Terrible software. Not only will it delete photos from the device without expres... |
| 181 | `942c4795-6c73-47ba...` | 1★ | `FAILURE` | `CANNOT_FIND_PHOTO` | `ALBUM_CONTAINER` | `STAGE_1_LEXICAL` | — | Whoever designed this was linguistically challenged. Stop using so many synonyms... |
| 182 | `3be20948-45e3-439e...` | 1★ | `FAILURE` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | face group doesn't work on my old android. I can't access the settings to turn i... |
| 183 | `e5f2c9a6-ad60-4029...` | 1★ | `FAILURE` | `REQUIRES_EXACT_DATE` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_2_SEMANTIC_EXPANSION` | — | Some photos randomly have a larger thumbnail in the main gallery view. This is v... |
| 184 | `55124187-bbcd-4c32...` | 1★ | `FAILURE` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_1_LEXICAL` | — | sharing photos to Gemini or Signal or other app doesn't work - literally nothing... |
| 185 | `c5a0669e-3256-4824...` | 1★ | `FAILURE` | `REQUIRES_EXACT_DATE` | `TEMPORAL_DATE` | `STAGE_1_LEXICAL` | — | The latest update is horrible. Photos used to have the most amazing AI search. T... |
| 186 | `d8a6e523-2eb2-499f...` | 2★ | `FAILURE` | `INCOMPLETE_RESULTS` | `SEARCH_KEYWORD` | `STAGE_1_LEXICAL` | — | The image search feature has actually gotten worse. |
| 187 | `f857a9d6-8057-49da...` | 2★ | `FAILURE` | `INCOMPLETE_RESULTS` | `SEARCH_KEYWORD` | `STAGE_1_LEXICAL` | — | i had no issues with this app until recently, this week to be precise, my entire... |
| 188 | `8248e690-792d-4c7d...` | 2★ | `FAILURE` | `CONTEXT_NOT_UNDERSTOOD` | `NATURAL_LANGUAGE_DESCRIPTION` | `STAGE_1_LEXICAL` | — | Lacking image search features and Gemini integration. |
| 189 | `1b8553c8-4868-49f3...` | 2★ | `FAILURE` | `PERSON_NOT_RECOGNIZED` | `PERSON_FACE` | `STAGE_1_LEXICAL` | — | has deleted whole faces without even asking me, and does a terrible job identify... |
| 190 | `rev-user-c...` | 2★ | `FAILURE` | `CANNOT_FIND_PHOTO` | `OBJECT_NAME` | `HISTORICAL_PRISTINE` | ✅ YES | AI Assisted search is not working on desktop It used to be that in the search ba... |

---

## Summary of Excluded Categories from Raw Pool (1,266 Reviews)

1. **Spam / Low Quality (< 4 words):** 363 reviews excluded (e.g. "nice", "good app", "bad update").
2. **Pure Cloud Storage / Payment Complaints:** 4 reviews excluded (e.g. "100 gb subscription fee is too high").
3. **Pure Photo / Video Editor Complaints:** 29 reviews excluded (e.g. "magic eraser ruined my photo background").
4. **Pure Crash on Launch Reports:** 4 reviews excluded (e.g. "app crashes immediately upon opening").
5. **General File Sync / Deletion Without Retrieval Context:** 866 reviews excluded (e.g. complaints regarding sync deleting local device copies when deleting from cloud, without any search or retrieval activity).
