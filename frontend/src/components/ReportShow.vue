<template>
  <div class="wrapper">
    <div>
      <div class="block-filters">
        <v-dialog max-width="900">
          <template v-slot:activator="{ props: activatorProps }">
            <v-btn
              v-bind="activatorProps"
              color="info"
              text="Фільтри"
              variant="flat"
              style="float: right;"
            ></v-btn>
            <v-btn
              @click="dumpdata"
              color="info"
              text="Завантажити"
              variant="flat"
              style="float: left;"
            ></v-btn>
          </template>
          <template v-slot:default="{ isActive }">
            <v-card>
              <v-card-title class="text-h4 grey lighten-2">
                Фільтри
              </v-card-title>

              <div class="filter-dialog-center" style="margin: 0 20px ">
                <div class="dialog-filters-cleaner">
                  <label for="" style="font-size: 14px;">Подавач</label>
                  <v-text-field v-model="filterUser"></v-text-field>
                </div>
                <div class="dialog-filters-rate" style="margin-top: 0; ">
                  <label for="" style="font-size: 14px;">Роки</label>
                  <v-select
                    :items="uniqueYears"
                    solo
                    dense
                    v-model="filterYears"
                  ></v-select>
                </div>
                <div class="dialog-filters-rate" style="margin-top: 0; ">
                  <label for="" style="font-size: 14px;">Тип перевірки</label>
                  <v-select
                    :items="uniqueCheckTypes"
                    solo
                    dense
                    v-model="filterCheckType"
                  ></v-select>
                </div>
                <div class="dialog-filters-rate" style="margin-top: 0; ">
                  <label for="" style="font-size: 14px;">Кафедра</label>
                  <v-autocomplete
                    dense
                    solo
                    :items="uniqueDepartments"
                    v-model="filterDepartment"
                  ></v-autocomplete>
                </div>
              </div>

              <v-card-actions>
                <v-btn
                  color="primary"
                  @click="() =>{
                    handleClearFilters();
                    isActive.value = false
                  }"
                >
                  Очистити фільтри
                </v-btn>
                <v-spacer></v-spacer>
                <v-btn
                  color="primary"
                  @click="() =>{
                    handleApplyFilters();
                    isActive.value = false;
                  }"
                >
                  Зберегти
                </v-btn>
              </v-card-actions>
            </v-card>
          </template>
        </v-dialog>
      </div>
      <h1 class="report-list-header">Результати</h1>
      <ul class="report-list-ul">
        <li v-for="report in reports" :key="report.id">
          <v-card
            class="mx-auto"
            min-width="400"
            hover
          >
            <v-card-item>
              <v-card-title>
                <b>Подавач:</b> {{ report.entry.submitter.name }} {{ report.entry.submitter.surname }} <br>
                <div class="entry-text"><b>Кафедра:</b> {{ report.entry.submitter.department }}</div>
                <div class="entry-text">
                  <span class="">{{report.entry.workkind.name}}</span>
                  <span class="">{{report.entry.workkind2.name}}</span>
                  <span class="">{{report.entry.workkind3.name}}</span>
                </div>
              </v-card-title>
            </v-card-item>
            <v-card-text v-if="report.entry.description" style="padding-bottom: 10px;">
              <div>{{report.entry.description}}</div>
            </v-card-text>
            <v-card-text style="padding-top: 0;">
              <b>Роки:</b> {{ report.entry.year }}<br>
              <b>Тип:</b> {{ report.check_type }}<br>
              <b>Результат: </b>{{ report.result }}<br>
              <b>ID в campus: </b>{{ report.entry.id }}
              <span @click="showDuplicateObject(report)" v-show="report.duplicate"><a>(Показати)</a></span>
            </v-card-text>
            <div v-show="!report.duplicate" @click="confirmReport(report.id)" class="button-confirm">Підтвердити</div>
          </v-card>
        </li>
      </ul>
      <div class="text-center pagination-block">
        <v-pagination
          v-model="page"
          :length="maxPage"
          :total-visible="7"
          @click="handlePaginationPress()"
        ></v-pagination>
      </div>
    </div>
    <v-dialog
      v-model="showDuplicate"
      width="950px"
    >
      <v-card
        class="mx-auto"
        min-width="900"
        hover
        v-if="duplicateObject"
      >
        <v-card-item>
          <v-card-title>
            <b>Подавач:</b> {{ duplicateObject.submitter.name }} {{ duplicateObject.submitter.surname }}
            <div class="entry-text"><b>Департамент:</b> {{ duplicateObject.submitter.department }}</div>
            <div class="entry-text">
              <span class="">{{duplicateObject.workkind.name}}</span>
              <span class="">{{duplicateObject.workkind2.name}}</span>
              <span class="">{{duplicateObject.workkind3.name}}</span>
            </div>
          </v-card-title>
        </v-card-item>
        <v-card-text v-if="duplicateObject.description" style="padding-bottom: 10px;">
          <div>{{duplicateObject.description}}</div>
        </v-card-text>
        <v-card-text style="padding-top: 0;">
          <b>Роки:</b> {{ duplicateObject.year }}<br>
          <b>ID в Campus:</b> {{ duplicateObject.id }}<br>
        </v-card-text>
      </v-card>
    </v-dialog>

  </div>
</template>

<script lang="ts">
import axios from '@/axios';
import { defineComponent, ref, onMounted } from "vue";

interface ResultData {
  unique_years: string[],
  unique_check_types: string[],
  unique_departments: string[]
}

interface Result{
  queryset: Report[],
  max_page: number

}

interface Duplicate {
  id: number;
  submitter: {
    name: string;
    surname: string;
    department: string
  };
  year: string;
  description: string;
  workkind: {
    id: number;
    name: string
  };
  workkind2: {
    id: number;
    name: string
  };
  workkind3: {
    id: number;
    name: string
  };
}

interface Report {
  id: number;
  check_type: string;
  result: string;
  entry: {
    id,
    submitter: {
      name: string;
      surname: string;
      department: string
    };
    year: string;
    description: string;
    workkind: {
      id: number;
      name: string
    };
    workkind2: {
      id: number;
      name: string
    };
    workkind3: {
      id: number;
      name: string
    };
  };
  duplicate: Duplicate
}

export default defineComponent({

  setup() {
    const reports = ref<Report[]>([]);
    const page = ref(1);
    const maxPage = ref(0);
    const filterUser = ref("");
    const icon = ref("mdi-emoticon");
    const marker = ref(true);
    const filterYears = ref("");
    const uniqueYears = ref([""])
    const showDuplicate = ref(false);
    const duplicateObject = ref<Duplicate>({
      description: '',
      id: 0,
      submitter: { department: '', name: '', surname: '' },
      workkind: { id: 0, name: '' },
      workkind2: { id: 0, name: '' },
      workkind3: { id: 0, name: '' },
      year: ''
    });
    const uniqueCheckTypes = ref<string[]>([]);
    const filterCheckType = ref("");
    const uniqueDepartments = ref<string[]>([]);
    const filterDepartment = ref("");
    const userFilters = ref<any>({});

    const fetchReportsData = async () => {

      try {
        const response = await axios.get<ResultData>(`/reports-data`);
        uniqueYears.value = response.data.unique_years;
        uniqueCheckTypes.value = response.data.unique_check_types;
        uniqueDepartments.value = response.data.unique_departments;
      } catch (error) {
        console.error('Error fetching reports data:', error);
      }
    };

    const fetchReports = async () => {

     let query = getFiltersQuery();

      try {
        const response = await axios.get<Result>(`/reports?page=${page.value}&filters=${query}`);
        reports.value = response.data.queryset;
        maxPage.value = response.data.max_page;
      } catch (error) {
        console.error('Error fetching reports:', error);
      }
    };

    const confirmReport = async (reportId: number) =>{
      try {
        const response = await axios.delete<Result>(`/api/delete-report/${reportId}`)
        await fetchReports()
      } catch (error) {
        console.error('Error fetching reports:', error);
      }
    };

    const getFiltersQuery = () =>{
      const keys = Object.keys(userFilters.value);
      let query:string[] = [];

      keys.forEach(el =>{
        if (userFilters.value[el]){
          query.push(`${el}@@@${userFilters.value[el]}`)
        }
      })

      return query.join("%%");
    }

    const handlePaginationPress = async (): Promise<void> => {
      await  fetchReports();
    };

    const showDuplicateObject = (report:Report) =>{
      duplicateObject.value = report.duplicate;
      showDuplicate.value = true;
    };

    const dumpdata = async () =>{
      let query = getFiltersQuery();
      const response = await axios.get<Result>(`/reports?filters=${query}&all=true`)
      const data = response.data.queryset
       if (!data) return;

      const jsonData = JSON.stringify(data, null, 2);
      const blob = new Blob([jsonData], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);

      const a = document.createElement('a');
      a.href = url;
      a.download = 'all_reports.json';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    }

    const handleApplyFilters = async () =>{
      userFilters.value = {
        entry__year: filterYears.value,
        check_type: filterCheckType.value,
        entry__submitter__department: filterDepartment.value,
        entry__submitter__full_name: filterUser.value
      }
      await  fetchReports();
    };

    const handleClearFilters = async () =>{

      filterYears.value = "";
      filterCheckType.value = "";
      filterDepartment.value = "";
      filterUser.value = "";

      userFilters.value = {
        entry__year: "",
        check_type: "",
        entry__submitter__department: "",
        entry__submitter__full_name: ""
      }
      await  fetchReports();
    };

    onMounted(() =>{
      fetchReports();
      fetchReportsData();
    });
    return {
      dumpdata,
      reports,
      page,
      handlePaginationPress,
      maxPage,
      filterUser,
      icon,
      marker,
      filterYears,
      uniqueYears,
      showDuplicate,
      showDuplicateObject,
      duplicateObject,
      uniqueCheckTypes,
      filterCheckType,
      uniqueDepartments,
      filterDepartment,
      handleApplyFilters,
      handleClearFilters,
      confirmReport
    };
  }
});
</script>
