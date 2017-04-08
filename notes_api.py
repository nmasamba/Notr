import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.ext import ndb

import models
import resources
import errors

package = 'notr-154615'

@endpoints.api(name='notr-154615', version='v2')
class NotesApi(remote.Service):
    NoteRequestContainer = endpoints.ResourceContainer(
        resources.NoteRepr, key=messages.StringField(1))

    @endpoints.method(message_types.VoidMessage,
                      resources.NoteCollection,
                      path='notr-154615',
                      http_method='GET',
                      name='notr-154615.notr-154615List')
    def note_list(self, request):
        items = []
        for note in models.Note.query().fetch():
            checklist_items = []
            for i in note.checklist_items:
                checklist_items.append(
                    resources.CheckListItemRepr(title=i.title,
                                                checked=i.checked))
            files = [f.urlsafe() for f in note.files]
            r = resources.NoteRepr(key=note.key.urlsafe(),
                                   title=note.title,
                                   content=note.content,
                                   date_created=note.date_created,
                                   checklist_items=checklist_items,
                                   files=files)
            items.append(r)

        return resources.NoteCollection(items=items)

    @endpoints.method(resources.NoteRepr,
                      resources.NoteRepr,
                      path='notr-154615',
                      http_method='POST',
                      name='notr-154615.notr-154615Create')
    def note_create(self, new_resource):
        user = endpoints.get_current_user()
        if user is None:
            raise endpoints.UnauthorizedException()

        note = models.Note(parent=ndb.Key("User", user.nickname()),
                           title=new_resource.title,
                           content=new_resource.content)
        note.put()
        new_resource.key = note.key.urlsafe()
        new_resource.date_created = note.date_created
        return new_resource

    @endpoints.method(resources.NoteCollection,
                      message_types.VoidMessage,
                      path='notr-154615',
                      http_method='PUT',
                      name='notr-154615.notr-154615BatchUpdate')
    def note_batch_update(self, request):
        for note_repr in request.items:
            note = ndb.Key(urlsafe=note_repr.key).get()
            note.title = note_repr.title
            note.content = note_repr.content

            checklist_items = []
            for item in note_repr.checklist_items:
                checklist_items.append(models.CheckListItem(title=item.title,
                                                            checked=item.checked))
            note.checklist_items = checklist_items

            files = []
            for file_id in note_repr.files:
                try:
                    files.append(ndb.Key(urlsafe=file_id).get())
                except TypeError:
                    continue
            note.files = files
            note.put()

        return message_types.VoidMessage()

    @endpoints.method(message_types.VoidMessage,
                      message_types.VoidMessage,
                      path='notr-154615',
                      http_method='DELETE',
                      name='notr-154615.notr-154615BatchDelete')
    def note_list_delete(self, request):
        # https://code.google.com/p/googleappengine/issues/detail?id=11371
        raise errors.MethodNotAllowed()

    @endpoints.method(NoteRequestContainer,
                      resources.NoteRepr,
                      path='notr-154615/{key}',
                      http_method='GET',
                      name='notr-154615.notr-154615Detail')
    def note_get(self, request):
        note = ndb.Key(urlsafe=request.key).get()
        checklist_items = []
        for i in note.checklist_items:
            checklist_items.append(
                resources.CheckListItemRepr(title=i.title,
                                            checked=i.checked))
        files = [f.urlsafe() for f in note.files]
        return resources.NoteRepr(key=request.key, title=note.title,
                                  content=note.content,
                                  date_created=note.date_created,
                                  checklist_items=checklist_items,
                                  files=files)

    @endpoints.method(NoteRequestContainer, message_types.VoidMessage,
                      path='notr-154615/{key}', http_method='POST',
                      name='notr-154615.notr-154615DetailPost')
    def note_get_post(self, request):
        raise errors.MethodNotAllowed()

    @endpoints.method(NoteRequestContainer, resources.NoteRepr,
                      path='notr-154615/{key}', http_method='PUT',
                      name='notr-154615.notr-154615Update')
    def note_update(self, request):
        note = ndb.Key(urlsafe=request.key).get()
        note.title = request.title
        note.content = request.content
        checklist_items = []
        for item in request.checklist_items:
            checklist_items.append(models.CheckListItem(title=item.title,
                                                        checked=item.checked))
        note.checklist_items = checklist_items

        files = []
        for file_id in request.files:
            try:
                files.append(ndb.Key(urlsafe=file_id).get())
            except TypeError:
                continue
        note.files = files
        note.put()
        return resources.NoteRepr(key=request.key, title=request.title,
                                  content=request.content,
                                  date_created=request.date_created,
                                  checklist_items=request.checklist_items,
                                  files=request.files)

    @endpoints.method(NoteRequestContainer, message_types.VoidMessage,
                      path='notr-154615/{key}', http_method='DELETE',
                      name='notr-154615.notr-154615Delete')
    def note_delete(self, request):
        ndb.Key(urlsafe=request.key).delete()
        return message_types.VoidMessage()

app = endpoints.api_server([NotesApi])
