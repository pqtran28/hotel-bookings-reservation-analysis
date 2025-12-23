import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# CONFIG

st.set_page_config(
    page_title='Hotel Cancellation Dashboard',
    page_icon=':bar_chart:',
    layout='wide'
)

st.header("Dashboard phân tích khả năng hủy đặt phòng khách sạn năm 2024")


@st.cache_data
def load_data(DATA_PATH):
    df = pd.read_csv(DATA_PATH)

    prev_map = {
        '0': 'Chưa lần nào',
        '1-5': 'Từ 1-5 lần',
        '>5': 'Trên 5 lần' 
    }
    df['previous_cancellations_group_label'] = df['previous_cancellations_group'].astype(str).map(prev_map)
    df['previous_bookings_not_canceled_group_label'] = df['previous_bookings_not_canceled_group'].astype(str).map(prev_map)


    df['is_canceled_label'] = df['is_canceled'].apply(lambda x: 'Hủy' if x == 1 else 'Không hủy')

    df['has_company_label'] = df['has_company'].apply(lambda x: 'Thông qua công ty' if x==1 else 'Không thông qua công ty')

    df['has_agent_label'] = df['has_agent'].apply(lambda x: 'Thông qua đại lý' if x==1 else 'Không thông qua đại lý')

    month_map = {
    'January': 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12
    }

    df['arrival_date_month'] = df['arrival_date_month'].map(month_map)
    df['arrival_date'] = df['arrival_date_day_of_month'].astype(str) + '/' + df['arrival_date_month'].astype(str) + '/' + df['arrival_date_year'].astype(str)
    df['arrival_date'] = pd.to_datetime(df['arrival_date'], format='mixed', errors='coerce')

    df['total_guests'] = df['total_guests'].astype(int)
    df['is_repeated_guest_group'] = df['is_repeated_guest'].apply(lambda x: 'Đã từng đặt phòng' if x == 1 else 'Chưa từng đặt phòng')

    top_countries = df['country'].value_counts()[(df['country'].value_counts() > 1000)].index

    df['country_group'] = df['country'].where(
        df['country'].isin(top_countries), 'Other'
    )

    df['is_different_room'] = (df['reserved_room_type'] != df['assigned_room_type']).astype(int).apply(lambda x: 'Khác phòng đã đặt' if x==1 else 'Giống phòng đã đặt')

    return df

# uploaded_file = st.file_uploader("Chọn 1 file để upload phân tích.\nĐịnh dạng yêu cầu: .csv")

# if uploaded_file is None:
#     st.stop()

uploaded_file = './data_processed_for_analysis.csv'

df = load_data(uploaded_file)
st.dataframe(df)

# =========== NGÀY THÁNG ===========

st.markdown("**Ngày khách đến/xác nhận hủy**")
df['arrival_date'] = pd.to_datetime(df['arrival_date'], format='mixed')

startDate = pd.to_datetime(df['arrival_date']).min()
endDate = pd.to_datetime(df['arrival_date']).max()

dateCol1, dateCol2 = st.columns((2))
with dateCol1:
    date_1 = pd.to_datetime(st.date_input("Bắt đầu",startDate))
with dateCol2:
    date_2 = pd.to_datetime(st.date_input("Kết thúc",endDate))

df = df[(df['arrival_date'] >= date_1) & (df['arrival_date'] <= date_2)].copy()

# ====================== TỔNG QUAN ===========================
st.subheader("Tổng quan")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Tổng số lượt đặt phòng",len(df))
col2.metric("Tỉ lệ hủy phòng (%)", round(df['is_canceled'].mean()*100,2))
col3.metric("Tổng số khách",df['total_guests'].sum())
col4.metric("Trung bình tiền đặt phòng",round(df['adr'].mean(),2))

col1, col2 = st.columns(2)

with col1:
    monthly = (
        df.groupby(['arrival_date_month', 'is_canceled_label'])
        .size()
        .reset_index(name='num_bookings')
    )

    fig = px.bar(monthly,
                x='arrival_date_month',y='num_bookings',
                color='is_canceled_label',
                barmode='group', # group/stack
                labels={
                    'arrival_date_month': 'Tháng',
                    'num_bookings': 'Số lượt đặt phòng',
                    'is_canceled_label': 'Hủy phòng'
                },
                title='Số lượt đặt phòng hàng tháng',
                text_auto=True,
                color_discrete_map={
                'Hủy': "#FAC6BB", 
                'Không hủy': "#FB8861"
                
        }
    )
    st.plotly_chart(fig,use_container_width=True)

with col2:
    fig = px.box(
        df,
        x="is_canceled_label",
        y="adr",
        color="is_canceled_label",
        points=False,
        title='Giá phòng trung bình mỗi ngày',
        labels= {
            'adr': 'Giá phòng trung bình',
            'is_canceled_label': 'Hủy phòng'
        }
    )

    st.plotly_chart(fig, use_container_width=True)



# ============== THEO LOẠI KHÁCH SẠN =====================================================================

st.subheader("Loại khách sạn và khả năng hủy đặt phòng")

hotel_type = st.selectbox("Chọn loại khách sạn", df['hotel_type'].unique().tolist() + ['Cả 2'])

if hotel_type != 'Cả 2':
    df_new = df[(df['arrival_date'] >= date_1) & (df['arrival_date'] <= date_2) & (df['hotel_type'] == hotel_type)].copy()
else:
    df_new = df[(df['arrival_date'] >= date_1) & (df['arrival_date'] <= date_2)].copy()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Tổng số lượt đặt phòng",len(df_new))
col2.metric("Tỉ lệ hủy phòng (%)", round(df_new['is_canceled'].mean()*100,2))
col3.metric("Tổng số khách",df_new['total_guests'].sum())
col4.metric("Trung bình tiền đặt phòng",round(df_new['adr'].mean(),2))

chart1, chart2, chart3 = st.columns([1.5,3,2.5])

# ============= BAR CHART LƯỢT ĐẶT, HỦY PHÒNG ================

with chart1:
    hotel_type_group = df_new.groupby('hotel_type')['total_guests'].sum().reset_index()

    fig = px.pie(hotel_type_group, 
                values='total_guests',names='hotel_type',
                title='Thị phần các loại khách sạn')
    fig.update_traces(text =  hotel_type_group["hotel_type"], textposition = "inside")
    st.plotly_chart(fig, use_container_width=True)

# ============= LINE CHART TỈ LỆ HỦY PHÒNG ================

with chart2:
    monthly_hotel_type = (
        df_new.groupby(['arrival_date_month', 'hotel_type', 'is_canceled'])
        .size()
        .reset_index(name="num_bookings")
    )

    monthly_hotel_type['ratio'] = (
        monthly_hotel_type['num_bookings'] /
        monthly_hotel_type.groupby(['arrival_date_month', 'hotel_type'])['num_bookings']
            .transform('sum')
    )

    fig = px.line(monthly_hotel_type[monthly_hotel_type['is_canceled'] == 1],
                x='arrival_date_month',y='ratio',
                color='hotel_type',
                labels={
                    'arrival_date_month': 'Tháng',
                    'ratio': 'Tỉ lệ'
                },
                color_discrete_map={
                'City': "#5BD9E0", 
                'Resort': "#1E768F"
        },
                title='Tỉ lệ hủy đặt phòng theo tháng các loại khách sạn',
                markers=True
    )

    fig.update_layout(
        template='plotly_white',
        font=dict(size=13),
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)

with chart3:
    hotel_type_group = df_new.groupby(['hotel_type','is_canceled_label']).size().reset_index(name='count')
    fig = px.bar(hotel_type_group, y='hotel_type', x='count',
                color='is_canceled_label',
                labels={
                    'hotel_type': 'Loại khách sạn',
                    'count': 'Số lượt đặt phòng',
                    'is_canceled_label': 'Hủy phòng'
                },
                text_auto=True,
                title='Số lượng đặt/hủy đặt phòng theo loại khách sạn'
    )
    st.plotly_chart(fig, use_container_width=True)

# ================ BOOKING BEHAVIOR (THEO KHÁCH HÀNG) =========================================================================


st.subheader("Phân khúc khách hàng và khả năng hủy đặt phòng")


# ======    TỔNG QUAN THEO PHÂN KHÚC ===========
chart1, chart2, chart3 = st.columns(3)

with chart1:
    num_deposit_type = df.groupby(['deposit_type', 'is_canceled_label']).size().reset_index(name='count')

    fig = px.bar(num_deposit_type,
                x='deposit_type', y='count',
                labels={
                    'deposit_type': 'Loại đặt cọc',
                    'count': 'Số lượng đặt phòng',
                    'is_canceled_label': 'Hủy phòng'
                },
                color='is_canceled_label',
                text_auto=True,
                title='Tình trạng đặt phòng theo loại đặt cọc'
                )
    st.plotly_chart(fig, use_container_width=True)

with chart2:

    num_customer_type = df.groupby(['customer_type', 'is_canceled_label']).size().reset_index(name='count')

    fig = px.bar(num_customer_type,
                x='customer_type', y='count',
                labels={
                    'customer_type': 'Loại khách hàng',
                    'count': 'Số lượng đặt phòng',
                    'is_canceled_label': 'Hủy phòng'
                },
                color='is_canceled_label',
                color_discrete_map={
                'Hủy': "#FAC6BB", 
                'Không hủy': "#FB8861"
                
        },
                text_auto=True,
                title='Tình trạng đặt phòng theo loại khách hàng'
                )
    st.plotly_chart(fig, use_container_width=True)

with chart3:

    num_distribution_channel = df.groupby(['distribution_channel', 'is_canceled_label']).size().reset_index(name='count')

    fig = px.bar(num_distribution_channel,
                x='distribution_channel', y='count',
                labels={
                    'distribution_channel': 'Kênh phân phối',
                    'count': 'Số lượng đặt phòng',
                    'is_canceled_label': 'Hủy phòng'
                },
                color='is_canceled_label',
                text_auto=True,
                title='Tình trạng đặt phòng theo kênh phân phối'
                )
    st.plotly_chart(fig, use_container_width=True)


chart1, chart2 = st.columns([2.5,7.5])

with chart1:

    num_market_segment = df.groupby(['market_segment', 'is_canceled_label']).size().reset_index(name='count')

    fig = px.pie(num_market_segment,
                names='market_segment', values='count',
                labels={
                    'market_segment': 'Kênh phân phối',
                    'count': 'Số lượng đặt phòng',
                },
                hole = 0.5,
                title='Thị phần của các phân khúc thị trường'
                )
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    treemap_df = (
    df.groupby(['market_segment','customer_type','is_canceled_label'])
        .size()
        .reset_index(name='count')
    )

    fig = px.treemap(
        treemap_df,
        path=['market_segment','customer_type', 'is_canceled_label'],
        values='count',
        color='is_canceled_label',
        hover_data=['count'],
        title='Thị phần thị trường theo loại khách hàng và tình trạng đặt phòng',
        color_discrete_map={
            'Không hủy': '#F7B2C4',
            'Hủy': '#B6DBE4'
        }
    )
    fig.update_traces(opacity=0.8)

    fig.update_layout(height=550)

    st.plotly_chart(fig,use_container_width=True)

# ============================ KHẢ NĂNG HỦY THEO CÁC YẾU TỐ KHÁC, LỌC THEO PHÂN KHÚC =========================

chart1,chart2,chart3= st.columns([2,6.5,3.5])

with chart1:
    st.markdown("**Lọc theo**")
    filter_deposit = st.multiselect("Chọn loại đặt cọc", df['deposit_type'].unique())

    filter_customer = st.multiselect("Chọn loại khách hàng", df['customer_type'].unique())

    filter_channel = st.multiselect("Chọn kênh phân phối", df['distribution_channel'].unique())

    filter_market = st.multiselect("Chọn phân khúc thị trường", df['market_segment'].unique())


filtered_df = df.copy()

if filter_deposit:
    filtered_df = filtered_df[filtered_df['deposit_type'].isin(filter_deposit)]

if filter_customer:
    filtered_df = filtered_df[filtered_df['customer_type'].isin(filter_customer)]

if filter_channel:
    filtered_df = filtered_df[filtered_df['distribution_channel'].isin(filter_channel)]

if filter_market:
    filtered_df = filtered_df[filtered_df['market_segment'].isin(filter_market)]

with chart2:
    country_cancellation = filtered_df.groupby(['country_group', 'is_canceled_label']).size().reset_index(name='count')

    fig = px.bar(country_cancellation,
                x='country_group', y='count',
                color='is_canceled_label',
                labels={
                    'country_group': 'Quốc gia của khách',
                    'count':'Số lượng đặt phòng',
                    'is_canceled_label': 'Hủy phòng'
                },
                color_discrete_map={
                'Hủy': "#FAC6BB", 
                'Không hủy': "#FB8861"
                
        },
                barmode='group',
                text_auto=True,
                title='Số lượng đặt phòng theo quốc gia của khách hàng',
    )

    st.plotly_chart(fig, use_container_width=True)

with chart3:
    repeat_guests = filtered_df.groupby(['is_repeated_guest_group','is_canceled_label']).size().reset_index(name='count')

    fig = px.bar(repeat_guests,
                y='count',
                x='is_repeated_guest_group',
                color='is_canceled_label',
                labels={
                    'is_repeated_guest_group': 'Khách đã từng đặt phòng',
                    'count': 'Số lượng đặt phòng',
                    'is_canceled_label': 'Hủy phòng'
                },
                text_auto=True,
                title='Số lượng đặt phòng theo lịch sử khách hàng',
                color_discrete_map={
                'Hủy': "#FAC6BB", 
                'Không hủy': "#FB8861"
                
        },
                barmode='group'
    )
    
    st.plotly_chart(fig,use_container_width=True)

# ========== KHẢ NĂNG HỦY THEO LỊCH SỬ HÀNH VI ĐẶT PHÒNG ============================

st.subheader("Lịch sử, hành vi khách hàng, đặc điểm lưu trú và khả năng hủy đặt phòng")

chart1, chart2, chart3 = st.columns(3)

with chart1:

    previous_cancellations = df.groupby(['previous_cancellations_group_label','is_canceled_label']).size().reset_index(name='count')

    fig = px.bar(previous_cancellations,
                x='previous_cancellations_group_label', y='count',
                color='is_canceled_label',
                barmode='group',
                text_auto=True,
                labels={
                    'previous_cancellations_group_label': 'Số lần hủy đặt phòng trước',
                    'count': 'Số lượng đặt phòng',
                    'is_canceled_label': 'Hủy phòng'
                })
    
    st.plotly_chart(fig, use_container_width=True)


with chart2:
    
    previous_not_canceled = df.groupby(['previous_bookings_not_canceled_group_label','is_canceled_label']).size().reset_index(name='count')

    fig = px.bar(previous_not_canceled,
                x='previous_bookings_not_canceled_group_label', y='count',
                color='is_canceled_label',
                barmode='group',
                text_auto=True,
                labels={
                    'previous_bookings_not_canceled_group_label': 'Số lần đặt mà không hủy',
                    'count': 'Số lượng đặt phòng',
                    'is_canceled_label': 'Hủy phòng'
                })
    
    st.plotly_chart(fig, use_container_width=True)

with chart3:

    order = {'no_wait': 1, 'short':2, 'medium':3, 'long':4, 'very_long':5}
    waiting_group = df.groupby(['days_in_waiting_list_group','is_canceled_label']).size().sort_index(key=lambda x: x.map(order)).reset_index(name='count')

    fig = px.bar(waiting_group,
                x='days_in_waiting_list_group', y='count',
                color='is_canceled_label',
                barmode='group',
                text_auto=True,
                labels={
                    'days_in_waiting_list_group': 'Số ngày trong danh sách chờ xác nhận',
                    'count': 'Số lượng đặt phòng',
                    'is_canceled_label': 'Hủy phòng'
                })
    
    
    st.plotly_chart(fig, use_container_width=True)


chart1, chart2= st.columns(2)

with chart1:

    total_stays = df.groupby(['total_stays', 'is_canceled_label']).size().reset_index(name='count')
    fig = px.bar(total_stays,x='total_stays',y='count',
                color='is_canceled_label',
                text_auto=True,
                title='Tình trạng phòng theo đêm lưu trú',
                labels={
                    'total_stays': 'Số đêm lưu trú',
                    'count': 'Số lượng đặt phòng',
                    'is_canceled_label': 'Hủy phòng'
                })
    st.plotly_chart(fig,use_container_width=True)

with chart2:

    diff_room = df.groupby(['is_different_room','is_canceled_label']).size().reset_index(name='count')
    fig = px.bar(diff_room,y='is_different_room',x='count',
                color='is_canceled_label',
                text_auto=True,
                title='Tình trạng phòng theo phòng được sắp xếp',
                orientation='h',
                barmode='group',
                labels={
                    'is_different_room': 'Phòng được sắp xếp',
                    'count': 'Số lượng đặt phòng',
                    'is_canceled_label': 'Hủy phòng'
                })
    st.plotly_chart(fig,use_container_width=True)

# ========== ẢNH HƯỞNG CỦA THỜI GIAN VÀ CÁC YẾU TỐ LIÊN QUAN ĐẾN KHẢ NĂNG HỦY ĐẶT PHÒNG =================

st.subheader("Tổng kết ảnh hưởng của các yếu tố quan trọng đến khả năng hủy đặt phòng")

st.markdown("**Ảnh hưởng của thời gian chờ nhận phòng theo loại đặt cọc đến khả năng hủy đặt phòng**")
chart1, chart2 = st.columns(2)

with chart1:
    fig = px.violin(df, x='deposit_type', y='lead_time', color='is_canceled_label',
                    labels= {
                        'deposit_type': 'Loại đặt cọc',
                        'lead_time': 'Thời gian chờ nhận phòng',
                        'is_canceled_label': 'Hủy phòng'
                    })
    st.plotly_chart(fig, use_container_width=True)

with chart2:

    fig = px.box(df, x='deposit_type', y='lead_time', color='is_canceled_label',
                 labels= {
                        'deposit_type': 'Loại đặt cọc',
                        'lead_time': 'Thời gian chờ nhận phòng',
                        'is_canceled_label': 'Hủy phòng'
                    },
                    color_discrete_map={
                'Hủy': "#FAC6BB", 
                'Không hủy': "#FB8861"
                
        })
    st.plotly_chart(fig, use_container_width=True)

chart1, chart2, chart3 = st.columns([2.5,3,3])

with chart1:
    grouped = df.groupby(['hotel_type', 'deposit_type', 'is_canceled_label']).size().reset_index(name='count')

    fig = px.bar(grouped, x='deposit_type',
                y = 'count',
                color='is_canceled_label',
                facet_col='hotel_type',
                barmode='relative',
                labels={
        'hotel_type': 'Loại khách sạn',
        'count': 'Số lượng đặt phòng',
        'is_canceled_label': 'Hủy phòng',
        'deposit_type': 'Loại đặt cọc'
    },
    title='Hủy phòng theo loại khách sạn & loại đặt cọc',
    text_auto=True,
    height=600
    )

    st.plotly_chart(fig, use_container_width=True)

with chart2:

    customer_prop = df.groupby(['deposit_type', 'customer_type']).size().reset_index(name='count')

    customer_prop['proportion'] = (customer_prop['count'] /customer_prop.groupby('deposit_type')['count'].transform('sum'))

    fig = px.bar(customer_prop, x='deposit_type', y='proportion',
                color = 'customer_type',
                barmode='relative',
                color_discrete_map= {
                    'Transient': "#43B3BD",
                    'Group': "#CE4C4C",
                    'Contract': "#EC9465",
                    'Transient-Party': "#4ED281"
                }, height=600,
                text_auto=True,
                labels={
                    'customer_type': 'Loại khách hàng',
                    'deposit_type': 'Loại đặt cọc',
                    'proportion': 'Tỉ lệ đặt phòng'
                }, title='Tỉ lệ đặt phòng của từng nhóm khách hàng trong các loại đặt cọc')
    
    st.plotly_chart(fig, use_container_width=True)
    
with chart3:


    distribution_prop = df.groupby(['deposit_type', 'distribution_channel']).size().reset_index(name='count')

    distribution_prop['proportion'] = (distribution_prop['count'] / distribution_prop.groupby('deposit_type')['count'].transform('sum'))

    fig = px.bar(distribution_prop, x='deposit_type', y='proportion',
                color = 'distribution_channel',
                barmode='relative',
                color_discrete_map= {
                    'Direct': "#43B3BD",
                    'Undefined': "#CE4C4C",
                    'Corporate': "#EC9465",
                    'TA/TO': "#4ED281",
                    'GDS': "#C77AE6"
                }, height=600,
                labels={
                    'distribution_channel': 'Kênh phân phối',
                    'deposit_type': 'Loại đặt cọc',
                    'proportion': 'Tỉ lệ đặt phòng'
                },
                text_auto=True, title='Tỉ lệ đặt phòng của từng kênh phân phối trong các loại đặt cọc')
    
    st.plotly_chart(fig, use_container_width=True)



















