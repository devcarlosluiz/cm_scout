from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Alert
from .forms import AlertForm


@login_required
def alert_list(request):
    alerts = Alert.objects.filter(user=request.user).select_related('league')
    return render(request, 'alerts/list.html', {'alerts': alerts})


@login_required
def alert_create(request):
    if request.method == 'POST':
        form = AlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.user = request.user
            alert.save()
            messages.success(request, 'Alerta criado com sucesso!')
            return redirect('alerts:list')
    else:
        form = AlertForm()
    return render(request, 'alerts/form.html', {'form': form, 'title': 'Criar Alerta'})


@login_required
def alert_edit(request, pk):
    alert = get_object_or_404(Alert, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AlertForm(request.POST, instance=alert)
        if form.is_valid():
            form.save()
            messages.success(request, 'Alerta atualizado!')
            return redirect('alerts:list')
    else:
        form = AlertForm(instance=alert)
    return render(request, 'alerts/form.html', {'form': form, 'title': 'Editar Alerta'})


@login_required
def alert_delete(request, pk):
    alert = get_object_or_404(Alert, pk=pk, user=request.user)
    if request.method == 'POST':
        alert.delete()
        messages.success(request, 'Alerta removido!')
        return redirect('alerts:list')
    return render(request, 'alerts/confirm_delete.html', {'alert': alert})


@login_required
def alert_toggle(request, pk):
    alert = get_object_or_404(Alert, pk=pk, user=request.user)
    alert.active = not alert.active
    alert.save(update_fields=['active'])
    status = 'ativado' if alert.active else 'desativado'
    messages.info(request, f'Alerta {status}.')
    return redirect('alerts:list')
